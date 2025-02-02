from flask import Blueprint, Response, jsonify
import pandas as pd
from joblib import load

# Create a Blueprint instance for fire prediction endpoints.
firePrediction = Blueprint('firePrediction', __name__)

def get_fire_severity(prob: float) -> str:
    """Map the predicted fire probability to a severity level.


    Arguments:
        prob -- The predicted fire probability.

    Returns:
        Severity level based on the probability thresholds.
    """
    if prob >= 0.9:
        return "medium"
    elif prob >= 0.7:
        return "high"
    else:
        return "low"

@firePrediction.route('/api/getFirePrediction', methods=['GET'])
def predict_fire() -> Response:
    """
    GET endpoint that:
      - Loads the pre-trained model.
      - Reads and processes the environmental data.
      - Generates fire predictions.
      - Returns the results as a JSON response along with model information.
    
    Returns:
        Response an object containing the status, fire predictions list, and model info.
    """
    try:
        # Load the saved model pipeline from the model folder.
        model_pipeline = load('model/fire_prediction_model.pkl')
        
        # Load future environmental data from the data folder.
        future_data = pd.read_csv("data/future_environmental_data.csv", parse_dates=['timestamp'])
        
        # Feature engineering: extract hour and month from the timestamp.
        future_data['hour'] = future_data['timestamp'].dt.hour
        future_data['month'] = future_data['timestamp'].dt.month
        
        # Prepare the feature set by dropping unused columns.
        X_future = future_data.drop(columns=['timestamp', 'latitude', 'longitude'])
        
        # Get the fire probability predictions (class 1 probability).
        fire_probabilities = model_pipeline.predict_proba(X_future)[:, 1]
        
        # Construct the prediction results.
        predictions = []
        for i, row in future_data.iterrows():
            predictions.append({
                "timestamp": row['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": row['latitude'],
                "longitude": row['longitude'],
                "fire_prob": float(fire_probabilities[i]),  # Ensure JSON serializable type
                "fire_severity": get_fire_severity(fire_probabilities[i])
            })
        
        # Results are based on our training
        model_info = {
            "average_accuracy": 0.8911764705882353,
            "average_f1_score": 0.8815359237536656,
            "number_of_iterations": 10
        }
        
        # Return a JSON response with both predictions and model info.
        return jsonify({
            "status": "success",
            "predictions": predictions,
            "model_info": model_info
        })
    
    except Exception as e:
        # Return an error response with details if something goes wrong.
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
