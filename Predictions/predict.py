import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from joblib import dump
from datetime import timedelta

# 1. Load the historical data
env_data = pd.read_csv("historical_environmental_data.csv", parse_dates=['timestamp'])
fire_data = pd.read_csv("historical_wildfiredata.csv", parse_dates=['timestamp', 'fire_start_time'])

# 2. Feature Engineering on environmental data: add hour and month
env_data['hour'] = env_data['timestamp'].dt.hour
env_data['month'] = env_data['timestamp'].dt.month

# 3. Label the data: initialize with 0 and then mark observations near a fire event as 1.
env_data['fire_occurrence'] = 0

# Filter fire_data to include only medium and high severity events.
fire_data = fire_data[fire_data['severity'].isin(['medium', 'high'])]

time_threshold = timedelta(hours=3)
distance_threshold = 0.3  # degrees

def mark_fire_occurrence(fire_row: pd.Series) -> None:
    """
    Marks fire occurrences in the environmental dataset based on spatial and temporal proximity.

    Arguments:
        fire_row (pd.Series): A row containing fire event data, including 'fire_start_time', 'latitude', and 'longitude'.

    Modifies:
        env_data (pd.DataFrame): Updates the 'fire_occurrence' column for entries within the time and distance thresholds.
    """
    fire_time: float = fire_row['fire_start_time']
    fire_lat: float = fire_row['latitude']
    fire_lon: float = fire_row['longitude']
    
    mask_time = (env_data['timestamp'] >= (fire_time - time_threshold)) & (env_data['timestamp'] <= (fire_time + time_threshold))
    subset = env_data[mask_time]
    
    mask_space = (np.abs(subset['latitude'] - fire_lat) < distance_threshold) & (np.abs(subset['longitude'] - fire_lon) < distance_threshold)
    indices = subset[mask_space].index
    
    env_data.loc[indices, 'fire_occurrence'] = 1

fire_data.apply(mark_fire_occurrence, axis=1)

num_fires = (env_data['fire_occurrence'] == 1).sum()
num_non_fires = num_fires  # using a 1:1 ratio
print('Num of fire occurrences:', num_fires)
print('Num of no fire occurrences kept:', num_non_fires)

# Save a copy of the full dataset to use in each run
original_data = env_data.copy()

# Cross validation runs for evaluation
num_runs = 10
total_accuracy = 0
total_f1 = 0

for run in range(num_runs):
    # Work on a fresh copy of the original data for each run
    data = original_data.copy()
    
    fire_occurrences_one = data[data['fire_occurrence'] == 1]
    fire_occurrences_zero = data[data['fire_occurrence'] == 0]
    
    # Sample negatives (varying the seed each run)
    sampled_rows = fire_occurrences_zero.sample(n=num_non_fires, random_state=run)
    
    # Combine and shuffle
    balanced_data = pd.concat([fire_occurrences_one, sampled_rows]).sample(frac=1, random_state=run).reset_index(drop=True)
    
    # Prepare features and target. Drop columns not used in prediction.
    X = balanced_data.drop(columns=['fire_occurrence', 'latitude', 'longitude', 'timestamp'])
    y = balanced_data['fire_occurrence']
    
    # Scale features (this step is done inside the pipeline below, but here for evaluation)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train-test split (using stratification due to imbalance)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=run, stratify=y)
    
    classifier = SVC(kernel='rbf', class_weight='balanced', probability=True)
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    total_accuracy += accuracy
    total_f1 += f1

print('Average accuracy over', num_runs, ': ', total_accuracy / num_runs)
print('Average f1 score over', num_runs, ': ', total_f1 / num_runs)

# ----- Train Final Model -----
# For the final model, we again balance the dataset (using random_state=0 for reproducibility)
data = original_data.copy()
fire_occurrences_one = data[data['fire_occurrence'] == 1]
fire_occurrences_zero = data[data['fire_occurrence'] == 0]
sampled_rows = fire_occurrences_zero.sample(n=num_non_fires, random_state=0)
balanced_data = pd.concat([fire_occurrences_one, sampled_rows]).sample(frac=1, random_state=0).reset_index(drop=True)

# Prepare features and target. (Drop non-feature columns.)
X_final = balanced_data.drop(columns=['fire_occurrence', 'latitude', 'longitude', 'timestamp'])
y_final = balanced_data['fire_occurrence']

# Create a pipeline that includes scaling and the classifier.
model_pipeline = make_pipeline(StandardScaler(),
                               SVC(kernel='rbf', class_weight='balanced', probability=True))
model_pipeline.fit(X_final, y_final)

# Save the trained model pipeline to a file
dump(model_pipeline, 'fire_prediction_model.pkl')
print("Model saved to fire_prediction_model.pkl")
