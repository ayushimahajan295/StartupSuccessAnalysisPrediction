from flask import Flask, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

# Load the trained model
model = joblib.load('random_forest_model.pkl')

@app.route('/')
def home():
    return "Startup Success Prediction API is running."

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse JSON from request
        input_data = request.get_json()

        # Convert JSON to DataFrame
        input_df = pd.DataFrame([input_data])

        # Make prediction
        prediction = model.predict(input_df)
        prediction_result = "Success" if prediction[0] == 1 else "Failure"

        return jsonify({
            "prediction": prediction_result
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
