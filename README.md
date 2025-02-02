# CONUHack2025
# Piaz Dari Khoone
Our Team's Repository for ConUHack 2025

# Wildfire Response and Prediction Backend

This backend application is built with Flask and serves two main functions:  
1. **Resource Deployment Optimization**: Processes current wildfire data to optimize the deployment of firefighting resources.  
2. **Fire Prediction**: Uses a pre-trained machine learning model to predict future wildfire occurrences based on environmental data.

The solution is designed for managing wildfire incidents and includes API endpoints for both immediate resource deployment and future fire prediction.

## Project Structure

project_root/ 
├── requirements.txt # List of required Python packages 
├── current_optimise.py # Logic for processing wildfire data for resource deployment 
├── main.py # Application entry point for the Flask backend 
├── Predictions/ # Files and scripts to train and save the machine learning model 
│ └── [training scripts and notebooks] 
├── data/ 
│ └── future_environmental_data.csv # Data required for the fire prediction API 
├── model/ 
│ └── fire_prediction_model.pkl # Pre-trained ML model for fire prediction 
└── routes/ 
├── init.py # Marks the routes folder as a Python package 
├── fireReport.py # API endpoint for processing wildfire reports (resource deployment) 
└── firePrediction.py # API endpoint for generating fire predictions

## Prerequisites

- **Python 3.8+**
- It is recommended to use a virtual environment.
- Required Python libraries (see `requirements.txt`):
  - Flask
  - flask-cors
  - pandas
  - joblib

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
2. **Set Up a Virtual Environment (Optional but Recommended):**

   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate


3. **Install Dependencies:**

   ```bash
    pip install -r requirements.txt
    Running the Application

## Start the Flask server by executing:
3. **Install Dependencies:**

   ```bash
    python main.py

By default, the server runs on port 5000. You can change the port by setting the PORT environment variable.

## API Endpoints

//TODO: - fill this

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For significant changes, open an issue first to discuss your ideas.
