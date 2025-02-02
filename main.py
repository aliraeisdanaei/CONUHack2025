import os
from flask import Flask
from flask_cors import CORS

# Import the blueprints from the Routes folder.
from Routes.fireReport import fireReport
from Routes.firePrediction import firePrediction

app = Flask(__name__)

# Register the blueprints.
app.register_blueprint(fireReport)
app.register_blueprint(firePrediction)

CORS(app)

if __name__ == '__main__':
    # Use Render's PORT environment variable or default to 5000.
    port = int(os.environ.get("PORT", 6985))
    app.run(host='0.0.0.0', port=port)
