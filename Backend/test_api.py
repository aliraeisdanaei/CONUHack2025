import requests
import json

def test_endpoints():
    base_url = 'http://localhost:5000/api'
    
    # Test POST endpoint
    print("\nTesting POST endpoint...")
    post_response = requests.post(f'{base_url}/data')
    print("POST Response:")
    print(json.dumps(post_response.json(), indent=2))
    
    # Test GET endpoint
    print("\nTesting GET endpoint...")
    get_response = requests.get(f'{base_url}/data')
    print("GET Response:")
    print(json.dumps(get_response.json(), indent=2))

if __name__ == "__main__":
    test_endpoints()