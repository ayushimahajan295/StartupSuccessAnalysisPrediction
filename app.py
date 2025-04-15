from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import pickle
import os
import hashlib
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout

# Path configurations
MODEL_PATH = 'model/model.pkl'
DB_PATH = 'data/startup.db'
POWERBI_PATH = 'powerbi_link.txt'

# Load model if exists
try:
    model = pickle.load(open(MODEL_PATH, 'rb')) if os.path.exists(MODEL_PATH) else None
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

@app.route('/user', methods=['GET', 'POST'])
def user():
    if not is_logged_in('user'):
        flash("Please log in to access this page", "error")
        return redirect(url_for('login'))

    prediction_result = None
    
    if request.method == 'POST':
        if model:
            # Get form data for prediction
            funding = int(request.form.get('funding', 0))
            accelerator = int(request.form.get('accelerator', 0))
            revenue = int(request.form.get('revenue', 0))
            
            # Make prediction
            try:
                input_data = [funding, accelerator, revenue]
                prediction = model.predict([input_data])[0]
                prediction_result = "Success" if prediction == 1 else "Failure"
                
                # Save prediction to database
                with get_db_connection() as conn:
                    conn.execute(
                        "INSERT INTO predictions (username, funding, accelerator, revenue, prediction) VALUES (?, ?, ?, ?, ?)",
                        (session['username'], funding, accelerator, revenue, prediction_result)
                    )
                    conn.commit()
                
                log_action(session['username'], f"Made prediction: {prediction_result}")
                
            except Exception as e:
                prediction_result = f"Error: {str(e)}"
        else:
            prediction_result = "Model not available"
    
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