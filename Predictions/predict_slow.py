import pandas as pd
import numpy as np
from geopy.distance import geodesic

HISTORICAL_ENVIRONMENTAL_FILEPATH = "../Data/historical_environmental_data.csv"
HISTORICAL_WILDFIRE_FILEPATH = "../Data/historical_wildfiredata.csv"

# Thresholds
DISTANCE_THRESHOLD = 10.0  # in km
TIME_THRESHOLD = pd.Timedelta(seconds=(60 * 60 * 2))  # 2 hour


# Function to find closest fire event within thresholds
def find_nearest_fire(env_row, fire_data, distance_threshold, time_threshold):
    for _, fire_row in fire_data.iterrows():
        dist = geodesic((env_row.latitude, env_row.longitude), 
                        (fire_row.latitude, fire_row.longitude)).km
        time_diff = abs(env_row.timestamp - fire_row.timestamp)
        if dist <= distance_threshold and time_diff <= time_threshold:
            return pd.Series([
                fire_row["fire_start_time"], 
                fire_row["location"], 
                fire_row["severity"],
                fire_row["latitude"], 
                fire_row["longitude"]
            ])
    return pd.Series([np.nan, np.nan, np.nan, np.nan, np.nan])  # No fire found

if __name__ == '__main__':
    environmental_data = pd.read_csv(HISTORICAL_ENVIRONMENTAL_FILEPATH)
    fire_data = pd.read_csv(HISTORICAL_WILDFIRE_FILEPATH)

    environmental_data = environmental_data.head(1000)

    # Convert timestamps to datetime format
    environmental_data["timestamp"] = pd.to_datetime(environmental_data["timestamp"])
    fire_data["timestamp"] = pd.to_datetime(fire_data["timestamp"])
    fire_data["fire_start_time"] = pd.to_datetime(fire_data["fire_start_time"])

    environmental_data[["fire_start_time", "fire_location", "fire_severity", "fire_latitude", "fire_longitude"]] = \
    environmental_data.apply(lambda row: find_nearest_fire(row, fire_data, DISTANCE_THRESHOLD, TIME_THRESHOLD), axis=1)


    print(environmental_data)