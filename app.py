from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import pickle
import os
import hashlib
from datetime import datetime, timedelta
import json
import pandas as pd
import joblib

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout

# Path configurations
MODEL_PATH = 'model/random_forest_model.pkl'
DB_PATH = 'data/startup.db'
POWERBI_PATH = 'powerbi_link.txt'

# Load model if exists
try:
    model = joblib.load(open(MODEL_PATH, 'rb')) if os.path.exists(MODEL_PATH) else None
    if model is None:
        print("Warning: ML model not found. Prediction functionality will be disabled.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Log user actions
def log_action(username, action):
    with get_db_connection() as conn:
        conn.execute("INSERT INTO logs (username, action) VALUES (?, ?)", (username, action))
        conn.commit()

# Check if user is logged in
def is_logged_in(role=None):
    if 'username' not in session:
        return False
    if role and session.get('role') != role:
        return False
    return True

# Get Power BI URL
def get_powerbi_url():
    try:
        if os.path.exists(POWERBI_PATH):
            with open(POWERBI_PATH, "r") as f:
                return f.read().strip()
        return "https://app.powerbi.com/view?r=YOUR_POWERBI_EMBED_LINK"
    except Exception as e:
        print(f"Error reading Power BI link: {e}")
        return "https://app.powerbi.com/view?r=YOUR_POWERBI_EMBED_LINK"

@app.route('/', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        # Redirect to appropriate dashboard if already logged in
        return redirect(url_for(session['role']))
    
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?", 
                (username, password)
            ).fetchone()
            
            if user:
                session.permanent = True
                session['username'] = username
                session['role'] = user['role']
                session['user_id'] = user['id']
                
                log_action(username, "Logged In")
                return redirect(url_for(user['role']))
            else:
                error = "Invalid username or password"
    
    return render_template('login.html', error=error)


@app.route('/predict', methods=['POST'])
def predict():
    if not is_logged_in('user'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"success": False, "prediction": "Not logged in"}, 401
        flash("Please log in to access this page", "error")
        return redirect(url_for('login'))

    if model is None:
        prediction_result = "Model not available"
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"success": False, "prediction": prediction_result}
        session['prediction_result'] = prediction_result
        return redirect(url_for('user'))

    try:
        # Exact feature list from training
        features = [
            'funding_total_usd', 'country_code', 'funding_rounds',
            'Software', 'Biotechnology', 'Mobile', 'Curated Web', 'E-Commerce',
            'Social Media', 'Advertising', 'Enterprise Software', 'Games',
            'Health Care', 'Services', 'Internet', 'Technology', 'Finance',
            'Analytics', 'Hardware + Software', 'Security', 'Clean Technology',
            'Semiconductors', 'Apps', 'Health and Wellness', 'SaaS',
            'Web Hosting', 'Video', 'Networking', 'Social Network Media',
            'age_at_first_funding', 'age_at_last_funding'
        ]

        # Build form data into dictionary
        input_data = {feature: int(request.form.get(feature, 0)) for feature in features}
        input_df = pd.DataFrame([input_data])[features]

        # Predict
        prediction = model.predict(input_df)
        prediction_result = "Success" if prediction[0] == 1 else "Failure"

        # Save to DB
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO predictions (username, funding, accelerator, revenue, prediction) VALUES (?, ?, ?, ?, ?)",
                (session['username'], input_data['funding_total_usd'], None, None, prediction_result)
            )
            conn.commit()

        log_action(session['username'], f"Made prediction: {prediction_result}")
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"success": True, "prediction": prediction_result}
            
        # Otherwise handle as before for non-AJAX requests
        session['prediction_result'] = prediction_result
        return redirect(url_for('user'))

    except Exception as e:
        error_message = f"Error: {str(e)}"
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"success": False, "prediction": error_message}
        session['prediction_result'] = error_message
        return redirect(url_for('user'))



@app.route('/user', methods=['GET'])
def user():
    if not is_logged_in('user'):
        flash("Please log in to access this page", "error")
        return redirect(url_for('login'))

    prediction_result = session.pop('prediction_result', None)  # Get prediction result once

    powerbi_url = get_powerbi_url()

    return render_template(
        'user.html',
        username=session['username'],
        powerbi_url=powerbi_url,
        prediction=prediction_result
    )




@app.route('/admin')
def admin():
    if not is_logged_in('admin'):
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        # Get recent logs
        logs = conn.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100").fetchall()
        
        # Get recent predictions
        predictions = conn.execute(
            "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 100"
        ).fetchall()
        
        # Get all users
        users = conn.execute("SELECT id, username, role, created_at FROM users").fetchall()

    return render_template(
        'admin.html', 
        username=session['username'],
        logs=logs,
        predictions=predictions,
        users=users
    )

@app.route('/logout')
def logout():
    if 'username' in session:
        log_action(session['username'], "Logged Out")
    
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('login.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('login.html', error="Internal server error"), 500

if __name__ == '__main__':
    # Check if database exists, if not suggest to run db_setup.py first
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run 'python db_setup.py' first.")
    app.run(debug=True)