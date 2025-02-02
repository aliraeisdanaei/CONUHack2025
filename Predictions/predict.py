import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from datetime import timedelta

# 1. Load the historical data
env_data = pd.read_csv("../Data/historical_environmental_data.csv", parse_dates=['timestamp'])
fire_data = pd.read_csv("../Data/historical_wildfiredata.csv", parse_dates=['timestamp', 'fire_start_time'])

# 2. Feature Engineering on environmental data:
#    Extract hour and month from the timestamp to capture diurnal and seasonal patterns.
env_data['hour'] = env_data['timestamp'].dt.hour
env_data['month'] = env_data['timestamp'].dt.month

# Optionally, you might also include location information:
# env_data['lat'] = env_data['latitude']
# env_data['lon'] = env_data['longitude']

# 3. Label the data: initialize with 0 and then mark observations that are near a fire event as 1.
env_data['fire_occurrence'] = 0

# Filter rows where 'severity' is 'medium' or 'high'
fire_data = fire_data[fire_data['severity'].isin(['medium', 'high'])]

# We use a ±3-hour time window and a simple spatial threshold (0.5°) to mark an observation.
time_threshold = timedelta(hours=3)
distance_threshold = 0.5  # degrees (roughly 50 km; adjust as needed)

def mark_fire_occurrence(fire_row):
    fire_time = fire_row['fire_start_time']
    fire_lat = fire_row['latitude']
    fire_lon = fire_row['longitude']
    # Find environmental readings within the time window
    mask_time = (env_data['timestamp'] >= (fire_time - time_threshold)) & (env_data['timestamp'] <= (fire_time + time_threshold))
    subset = env_data[mask_time]
    # Further filter by spatial proximity (absolute difference on lat/lon)
    mask_space = (np.abs(subset['latitude'] - fire_lat) < distance_threshold) & (np.abs(subset['longitude'] - fire_lon) < distance_threshold)
    indices = subset[mask_space].index
    env_data.loc[indices, 'fire_occurrence'] = 1

# Apply the labeling for each wildfire event.
fire_data.apply(mark_fire_occurrence, axis=1)

num_fires = (env_data['fire_occurrence'] == 1).sum()
num_non_fires = int(1 * num_fires)
print('Num of fire occurrences:', num_fires)
print('Num of no fire occurences kept:', num_non_fires)


num_runs = 5
total_accurracy = 0
total_f1 = 0
for _ in range(num_runs):

    # Filter rows where 'fire_occurrences' is 1 and 0
    fire_occurrences_one = env_data[env_data['fire_occurrence'] == 1]
    fire_occurrences_zero = env_data[env_data['fire_occurrence'] == 0]

    # Randomly sample num_non_fires rows from those where 'fire_occurrences' is 0
    sampled_rows = fire_occurrences_zero.sample(n=num_non_fires, random_state=42)

    # Append the sampled rows to the rows where 'fire_occurrences' is 1
    env_data = pd.concat([fire_occurrences_one, sampled_rows])

    # Shuffle the combined data (if you want random order)
    env_data = env_data.sample(frac=1).reset_index(drop=True)

    # print(env_data)

    X = env_data.drop(columns=['fire_occurrence', 'latitude', 'longitude', 'timestamp'])
    y = env_data['fire_occurrence']

    # print(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    classifier = SVC(kernel='rbf')

    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # print("Accuracy:", accuracy)
    # print("Confusion Matrix:\n", conf_matrix)
    # print(f"F1-score: {f1}")

    total_accurracy += accuracy
    total_f1 += f1

print('Avergae accuracy over', num_runs, ': ', total_accurracy / num_runs)
print('Avergae f1 score over', num_runs, ': ', total_f1 / num_runs)

