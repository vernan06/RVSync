import urllib.request
import json

BASE_URL = "http://127.0.0.1:8080"
EMAIL = "admin@rvce.edu.in"
PASSWORD = "admin123"

def test_login():
    url = f"{BASE_URL}/api/auth/login/json"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        print(f"Sending POST to {url} with {EMAIL}")
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            
            print(f"Status Code: {status_code}")
            print(f"Response: {response_body}")
            
            if status_code == 200:
                print("Login SUCCESS")
                token_data = json.loads(response_body)
                token = token_data.get('access_token')
                print(f"Token received: {token[:20]}...")
                
                # Verify /api/users/profile/me
                print("\nVerifying profile...")
                profile_url = f"{BASE_URL}/api/users/profile/me"
                profile_req = urllib.request.Request(profile_url, headers={
                    'Authorization': f"Bearer {token}",
                    'Content-Type': 'application/json'
                })
                with urllib.request.urlopen(profile_req) as p_res:
                    print(f"Profile Status: {p_res.getcode()}")
                    print(f"Profile Data: {p_res.read().decode('utf-8')}")
            else:
                 print("Login FAILED")

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
