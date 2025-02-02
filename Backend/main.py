# main.py
from fastapi import FastAPI, File, UploadFile
import uvicorn
import pandas as pd
import os

from current_optimise import DATA_FILENAME, read_csv
from current_optimise import process_data, simulate_deployment

app = FastAPI(title="Wildfire Simulation API")

@app.get("/")
def read_root():
    return {"message": "Wildfire Simulation API is running!"}

@app.post("/simulate/")
# async def simulate(file: UploadFile = File(...)):
async def simulate():
    """
    Upload a CSV file (for example, current wildfire data) and run the simulation.
    The CSV file will be saved temporarily as 'current_wildfiredata.csv' (you can change this as needed).
    Then, the simulation code in samp.py is executed.
    """

    try:
        data = read_csv(DATA_FILENAME)
        process_data(data)

        report, logs = simulate_deployment(data)
        return report, logs
    except Exception as e:
        return {"error": str(e)}

# An endpoint to simply get the latest simulation report, if you store it globally
# (For simplicity, we only demonstrate the /simulate/ endpoint in this example.)

if __name__ == "__main__":
    # Run the server on port 8000 and listen on all interfaces (so it can be reached from your iPhone)
    uvicorn.run(app, host="0.0.0.0", port=8000)
