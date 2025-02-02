# Flask Backend API

This is a simple Flask backend that handles JSON data.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
flask run
```

## API Endpoints

### POST /api/data
Accepts JSON data and returns it with a success message.

Example request:
```bash
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### GET /api/health
Health check endpoint.

Example request:
```bash
curl http://localhost:5000/api/health
```