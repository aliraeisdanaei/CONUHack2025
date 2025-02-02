# from flask import Blueprint, request, Response, jsonify
from typing import List, Tuple
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create a Blueprint instance
# fireReport = Blueprint('fireReport', __name__)

RESOURCE_SPECS = {
    "Smoke Jumpers": {"deployment_minutes": 30, "operational_cost": 5000, "count": 5},
    "Fire Engines": {"deployment_minutes": 60, "operational_cost": 2000, "count": 10},
    "Helicopters": {"deployment_minutes": 45, "operational_cost": 8000, "count": 3},
    "Tanker Planes": {"deployment_minutes": 120, "operational_cost": 15000, "count": 2},
    "Ground Crews": {"deployment_minutes": 90, "operational_cost": 3000, "count": 8}
}

DAMADE_COSTS = {
    "low": 50000,
    "medium": 100000,
    "high": 200000
}

# -------------------------------
# Create a pool of resource units (non-reusable)
# -------------------------------
RESOURCE_POOL = []
for r_type, spec in RESOURCE_SPECS.items():
    for _ in range(spec["count"]):
        RESOURCE_POOL.append({
            "resource_type": r_type,
            "deployment_minutes": spec["deployment_minutes"],
            "operational_cost": spec["operational_cost"]
        })


def select_resource(resource_pool: list[dict], severity: str) -> dict:
    """Given a list of available resource units and the event severity,
    select one unit based on a severity-dependent heuristic.

    Arguments:
        resource_pool -- the list of resources available
        severity -- the severity of the event

    Returns:
        a unit that is available in the form of a dictionary
    """
    if severity == "high":
        resource_pool.sort(key=lambda r: (
            r["deployment_minutes"], r["operational_cost"]))
        return resource_pool[0]
    elif severity == "low":
        resource_pool.sort(key=lambda r: (
            r["operational_cost"], r["deployment_minutes"]))
        return resource_pool[0]
    elif severity == "medium":
        factor = 50  # factor to convert minutes to an equivalent cost
        resource_pool.sort(key=lambda r: (
            r["operational_cost"] + factor * r["deployment_minutes"]))
        return resource_pool[0]
    else:
        resource_pool.sort(key=lambda r: (
            r["operational_cost"], r["deployment_minutes"]))
        return resource_pool[0]


def simulate_deployment(
        wildfire_data: list[dict], resource_pool=RESOURCE_POOL) -> Tuple[list[dict], list[dict]]:
    """Simulates the deployment of wilfire events
    each resource is used only once

    Arguments:
        wildfire_data -- the list of sorted wildfire events
        resource_pool -- the list of resources available

    Policy change: For low severity events, intentionally "miss" (i.e. do not assign a resource)
    for the first low occurrences where the resource pool is lower than the number of events

    Returns:
        A tuple of the reports and an incident log for each of the events
    """
    total_operational_cost = 0
    total_damage_cost = 0
    addressed_count = 0
    missed_count = 0

    # Counters per severity:
    addressed_by_severity = {"low": 0, "medium": 0, "high": 0}
    missed_by_severity = {"low": 0, "medium": 0, "high": 0}

    # Policy: keep track of how many low severity events have been
    # intentionally missed.
    allowed_low_misses = max(0, len(wildfire_data) - len(resource_pool))
    low_missed_count = 0

    # List to log each incident
    incident_logs = []

    # Process each event one by one
    for idx, event in enumerate(wildfire_data):
        severity = event['severity'].lower()  # ensure lower-case
        event_time = event['timestamp']
        location = event.get('location', 'Unknown')

        log_entry = {
            "event_index": idx,
            "timestamp": event_time,
            "severity": severity,
            "location": location,
            "action": None,  # Will be updated below
            "resource": None,  # The unit assigned (if any)
            "operational_cost": 0
        }

        # --- Intentional miss policy for low severity events ---
        if severity == "low" and low_missed_count < allowed_low_misses:
            low_missed_count += 1
            missed_count += 1
            total_damage_cost += DAMADE_COSTS.get(severity, 0)
            missed_by_severity[severity] += 1
            log_entry["action"] = f"Missed (allowed low miss #{low_missed_count})"
            incident_logs.append(log_entry)
            continue

        # Normal processing: assign a resource if available
        if not resource_pool:
            # No resource available; mark as missed response
            missed_count += 1
            total_damage_cost += DAMADE_COSTS.get(severity, 0)
            missed_by_severity[severity] += 1
            log_entry["action"] = "Missed (no resources)"
        else:
            # Select a resource unit using the severity-dependent heuristic
            selected = select_resource(resource_pool, severity)
            # Non-reusable: remove from pool
            resource_pool.remove(selected)
            total_operational_cost += selected["operational_cost"]
            addressed_count += 1
            addressed_by_severity[severity] += 1
            log_entry["action"] = "Assigned"
            log_entry["resource"] = selected["resource_type"]
            log_entry["operational_cost"] = selected["operational_cost"]

        incident_logs.append(log_entry)

    # Prepare the summary report dictionary
    report = {
        "fires_addressed": addressed_by_severity,
        "fires_delayed": missed_by_severity,
        "operational_costs": total_operational_cost,
        "estimated_damage_costs": total_damage_cost,
    }

    return report, incident_logs

def sort_data(wildfire_data: list[dict]) -> None:
    """Sorts wildfire data in places by report time; if same time,
        then high severity events first

    Arguments:
        wildfire_data -- the list of wildfire events

    Modifies:
        wildfire_data -- then sorts the data by the dates
    """
    severity_order = {"high": 1, "medium": 2, "low": 3}
    wildfire_data.sort(key=lambda x: (
        x["timestamp"], severity_order[x["severity"]]))



def process_data(wildfire_data: list[dict]) -> None:
    """Processes the wildfire data in place

    Arguments:
        wildfire_data -- the list of wildfire events
    
    Modifies:
        wildfire_data -- converts all the date fields (timestamp, fire_start_time) in format of DATE_FORMAT to datetime
            then sorts the data by the dates
    """
    for event in wildfire_data:
        event['timestamp'] = datetime.strptime(event['timestamp'], DATE_FORMAT)
        event['fire_start_time'] = datetime.strptime(
            event['fire_start_time'], DATE_FORMAT)
    sort_data(wildfire_data)


# @fireReport.route('/api/makeFireReport', methods=['POST'])
# def post_data() -> Response:
#     """
#     GET Endpoint that 
#         - processes the csv data of the wildfire report
#         - Generates a report and an incident logo
#         - Returns the result as a JSON Object

#     Returns:
#         Response an object containing status, report, logs, and message
#     """
#     try:
#         # Get JSON data from request
#         data = request.get_json()
        
#         if not data:
#             return jsonify({
#                 "status": "error",
#                 "message": "No JSON data received"
#             }), 400
        
#         process_data(data)
#         report, logs = simulate_deployment(data)
        
#         return jsonify({
#             "status": "success",
#             "report": report, 
#             "logs": logs,
#             "message": "Data processed successfully"
#         })
        
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500

import csv
DATA_FILENAME = "./current_wildfiredata.csv"


def print_incident_report(incident_logs: list[dict]) -> None:
    """Prints incident report in a structured format.

    Arguments:
        incident_logs -- the incident log to print
    """
    print("\n----- Detailed Incident Report -----")
    for log in incident_logs:
        event_info = (
            f"Event {log['event_index']} | Time: {log['timestamp']} | "
            f"Severity: {log['severity'].capitalize()} | Location: {log['location']}"
        )

        if log["action"].startswith("Assigned"):
            unit_info = (
                f"--> Assigned Unit: {log['resource']} "
                f"(Cost: ${log['operational_cost']})"
            )
        else:
            unit_info = f"--> {log['action']}"
        print(f"{event_info} {unit_info}")


def print_summary_report(report: list[dict]) -> None:
    """ Prints the wildfire response summary report in a structured format.

    Arguments:
        report -- A dictionary containing fire response data.
    """
    print("----- Wildfire Response Report -----")
    print("Fires Addressed:")
    for severity, count in report["fires_addressed"].items():
        print(f"  {severity.capitalize()}: {count}")

    print("\nFires Delayed:")
    for severity, count in report["fires_delayed"].items():
        print(f"  {severity.capitalize()}: {count}")

    print(f"\nTotal Operational Costs: ${report['operational_costs']:,.2f}")
    print("Estimated Damage Costs from Delayed" \
        f"Responses: ${report['estimated_damage_costs']:,.2f}")

def read_csv(csv_filename: str) -> list[dict]:
    """Reads the csv file and returns a data as a list of dict

    Arguments:
        csv_filename -- the filepath to the csv file

    Returns:
        the wildfire data
    """
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        data = [row for row in csvreader]
    return data

if __name__ == "__main__":
    # try:
    wildfire_json = read_csv(DATA_FILENAME)
    # except Exception as e:
    #     print("Error reading the CSV file:", e)
    #     exit(1)

    report, incident_logs = simulate_deployment(wildfire_json, RESOURCE_POOL)

    print_summary_report(report)
    # print_incident_report(incident_logs)