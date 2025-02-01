import os
import json
import pandas as pd
from datetime import datetime

# -------------------------------
# Define our firefighting resources and damage costs
# -------------------------------
resource_specs = {
    "Smoke Jumpers": {"deployment_minutes": 30, "operational_cost": 5000, "count": 5},
    "Fire Engines": {"deployment_minutes": 60, "operational_cost": 2000, "count": 10},
    "Helicopters": {"deployment_minutes": 45, "operational_cost": 8000, "count": 3},
    "Tanker Planes": {"deployment_minutes": 120, "operational_cost": 15000, "count": 2},
    "Ground Crews": {"deployment_minutes": 90, "operational_cost": 3000, "count": 8}
}

damage_costs = {
    "low": 50000,
    "medium": 100000,
    "high": 200000
}

# -------------------------------
# Build the base resource pool (non-reusable)
# -------------------------------
def build_resource_pool():
    pool = []
    for r_type, spec in resource_specs.items():
        for _ in range(spec["count"]):
            pool.append({
                "resource_type": r_type,
                "deployment_minutes": spec["deployment_minutes"],
                "operational_cost": spec["operational_cost"]
            })
    return pool

# -------------------------------
# Heuristic for selecting a resource for a given event
# -------------------------------
def select_resource(available_resources, severity):
    """
    For high severity: choose the fastest (smallest deployment_minutes) unit.
    For low severity: choose the cheapest unit.
    For medium severity: choose based on a weighted sum (cost + factor * deployment_minutes).
    """
    if severity == "high":
        available_resources.sort(key=lambda r: (r["deployment_minutes"], r["operational_cost"]))
        return available_resources[0]
    elif severity == "low":
        available_resources.sort(key=lambda r: (r["operational_cost"], r["deployment_minutes"]))
        return available_resources[0]
    elif severity == "medium":
        factor = 50  # conversion factor from minutes to cost equivalent
        available_resources.sort(key=lambda r: (r["operational_cost"] + factor * r["deployment_minutes"]))
        return available_resources[0]
    else:
        available_resources.sort(key=lambda r: (r["operational_cost"], r["deployment_minutes"]))
        return available_resources[0]

# -------------------------------
# Helper: Compute dynamic reserve for an event
# -------------------------------
def compute_dynamic_reserve(event_time, severity, initial_resource_count, reserve_ratios, season_start, season_end):
    total_seconds = (season_end - season_start).total_seconds()
    progress = (event_time - season_start).total_seconds() / max(total_seconds, 1)
    season_progress = max(0.0, min(progress, 1.0))
    reserve_ratio = reserve_ratios.get(severity, 0.0)
    dynamic_reserve = int(initial_resource_count * (1 - season_progress) * reserve_ratio)
    return season_progress, dynamic_reserve

# -------------------------------
# Reserve saving/loading functions
# -------------------------------
def load_previous_reserve(filename="reserve_resources.json"):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                reserve = json.load(f)
            print(f"Loaded {len(reserve)} reserve resources from previous season.")
            return reserve
        except Exception as e:
            print("Error loading previous reserve:", e)
    return []

def save_current_reserve(available_resources, filename="reserve_resources.json"):
    try:
        with open(filename, "w") as f:
            json.dump(available_resources, f)
        print(f"Saved {len(available_resources)} reserve resources for next season.")
    except Exception as e:
        print("Error saving current reserve:", e)

# -------------------------------
# Simulation function
# -------------------------------
def simulate_deployment(
    df_events,
    reserve_ratios={"low": 0.5, "medium": 0.3, "high": 0.0},
    season_start=datetime(2024, 6, 1),
    season_end=datetime(2024, 9, 30, 23, 59, 59),
    include_previous_reserve=False,
    save_reserve=True,
    low_severity_cost_threshold=3000,
    medium_severity_cost_threshold=5000
):
    """
    Simulate resource assignment over events using a dynamic reserve policy.
      - For low/medium severity events, if available resources are low (or filtered resources are low),
        the event is intentionally missed.
      - High severity events always get a resource if available.
    Optionally load previous season's reserve and save remaining resources for the next season.
    """
    # Build the base pool and optionally add previous reserve
    base_pool = build_resource_pool()
    if include_previous_reserve:
        previous_reserve = load_previous_reserve()
        available_resources = base_pool + previous_reserve
    else:
        available_resources = base_pool.copy()
    
    initial_resource_count = len(available_resources)
    
    # Convert timestamp columns to datetime objects
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'])
    df_events['fire_start_time'] = pd.to_datetime(df_events['fire_start_time'])
    
    # Sort events by timestamp and severity (high severity first if same timestamp)
    severity_order = {"high": 0, "medium": 1, "low": 2}
    df_events.sort_values(
        by=["timestamp", "severity"],
        key=lambda col: col.map(severity_order) if col.name == "severity" else col,
        inplace=True
    )
    
    total_operational_cost = 0
    total_damage_cost = 0
    addressed_count = 0
    missed_count = 0
    addressed_by_severity = {"low": 0, "medium": 0, "high": 0}
    missed_by_severity = {"low": 0, "medium": 0, "high": 0}
    resource_usage = {rtype: 0 for rtype in resource_specs.keys()}
    incident_logs = []
    
    # Process each event in order
    for idx, event in df_events.iterrows():
        severity = event['severity'].lower()
        event_time = event['timestamp']
        location = event.get('location', 'Unknown')
        
        # Compute dynamic reserve
        season_progress, dynamic_reserve = compute_dynamic_reserve(
            event_time, severity, initial_resource_count, reserve_ratios, season_start, season_end)
        
        log_entry = {
            "event_index": idx,
            "timestamp": str(event_time),
            "severity": severity,
            "location": location,
            "season_progress": f"{season_progress:.2f}",
            "dynamic_reserve": dynamic_reserve,
            "action": None,
            "resource": None,
            "operational_cost": 0
        }
        
        # If available resources are at or below the dynamic reserve, miss the event
        if len(available_resources) <= dynamic_reserve:
            missed_count += 1
            total_damage_cost += damage_costs.get(severity, 0)
            missed_by_severity[severity] += 1
            log_entry["action"] = (f"Missed (reserve active: available={len(available_resources)}, "
                                   f"required > {dynamic_reserve})")
            incident_logs.append(log_entry)
            continue

        # Hold high-cost units for low/medium events
        if severity == "low":
            filtered_resources = [r for r in available_resources if r["operational_cost"] <= low_severity_cost_threshold]
            if not filtered_resources:
                filtered_resources = available_resources
        elif severity == "medium":
            filtered_resources = [r for r in available_resources if r["operational_cost"] <= medium_severity_cost_threshold]
            if not filtered_resources:
                filtered_resources = available_resources
        else:
            filtered_resources = available_resources
        
        # Assign a resource if one is available from the filtered list
        if filtered_resources:
            selected = select_resource(filtered_resources, severity)
            available_resources.remove(selected)
            total_operational_cost += selected["operational_cost"]
            addressed_count += 1
            addressed_by_severity[severity] += 1
            resource_usage[selected["resource_type"]] += 1
            
            log_entry["action"] = "Assigned"
            log_entry["resource"] = selected["resource_type"]
            log_entry["operational_cost"] = selected["operational_cost"]
        else:
            missed_count += 1
            total_damage_cost += damage_costs.get(severity, 0)
            missed_by_severity[severity] += 1
            log_entry["action"] = "Missed (no resources)"
        
        incident_logs.append(log_entry)
    
    # Prepare the summary report
    report = {
        "Number of fires addressed": addressed_count,
        "Number of fires delayed (missed responses)": missed_count,
        "Total operational costs": total_operational_cost,
        "Estimated damage costs from delayed responses": total_damage_cost,
        "Fire severity report": {
            "addressed": addressed_by_severity,
            "missed": missed_by_severity
        },
        "Resource usage by type": resource_usage,
        "Remaining resources": len(available_resources)
    }
    
    # Save remaining resources for next season if desired
    if save_reserve:
        save_current_reserve(available_resources)
    
    return report, incident_logs
