from current_optimise import process_data, simulate_deployment
from Routes.fireReport import fireReport  # Import the Blueprint, not the function

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
# Register the fireReport blueprint
app.register_blueprint(fireReport)

CORS(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)