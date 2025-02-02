import os

from Routes.fireReport import fireReport  # Import the Blueprint, not the function

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
# Register the fireReport blueprint
app.register_blueprint(fireReport)

CORS(app)

if __name__ == '__main__':
    # Use Render's PORT environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)