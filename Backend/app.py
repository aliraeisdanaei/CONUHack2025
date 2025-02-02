from current_optimise import DATA_FILENAME, read_csv
from current_optimise import process_data, simulate_deployment


data = read_csv(DATA_FILENAME)
process_data(data)

report, logs = simulate_deployment(data)



from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Store data temporarily (in a real application, you'd use a database)
data_store = {}

@app.route('/api/makeFireReport', methods=['POST'])
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
        simulate_deployment(data)
        
        return jsonify({
            "status": "success",
            "data": data,
            "message": "Data processed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)