from flask import Blueprint, request, jsonify
from current_optimise import process_data, simulate_deployment

# Create a Blueprint instance
fireReport = Blueprint('fireReport', __name__)

@fireReport.route('/api/makeFireReport', methods=['POST'])
def post_data():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        print(data)
        process_data(data)
        report, logs = simulate_deployment(data)
        
        return jsonify({
            "status": "success",
            "report": report, 
            "logs": logs,
            "message": "Data processed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
