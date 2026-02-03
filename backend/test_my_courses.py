import urllib.request
import json

BASE_URL = "http://127.0.0.1:8080"
EMAIL = "admin@rvce.edu.in"
PASSWORD = "admin123"

def test_my_courses():
    # 1. Login
    login_url = f"{BASE_URL}/api/auth/login/json"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(login_url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            if response.getcode() != 200:
                print("Login failed")
                return
            
            token_data = json.loads(response.read().decode('utf-8'))
            token = token_data.get('access_token')
            print("Login SUCCESS")

    except Exception as e:
        print(f"Login Error: {e}")
        return

    # 2. Get Classrooms and Enroll
    try:
        # Search for CSE-2E
        # Endpoint logic from frontend analysis: /api/classroom/list/by-branch?branch=CSE&year_level=SECOND
        search_url = f"{BASE_URL}/api/classroom/list/by-branch?branch=CSE&year_level=SECOND"
        req = urllib.request.Request(search_url, headers={
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        })
        
        classroom_id = None
        with urllib.request.urlopen(req) as response:
            classrooms = json.loads(response.read().decode('utf-8'))
            print(f"Found {len(classrooms)} classrooms.")
            if classrooms:
                target_cls = classrooms[0] # Just pick first one, or search for specific
                classroom_id = target_cls['id']
                print(f"Enrolling in Classroom ID: {classroom_id} ({target_cls['code']})")
                
                # Enroll endpoint: POST /api/classroom/{id}/enroll
                enroll_url = f"{BASE_URL}/api/classroom/{classroom_id}/enroll"
                enroll_req = urllib.request.Request(enroll_url, method='POST', headers={
                    'Authorization': f"Bearer {token}",
                    'Content-Type': 'application/json'
                })
                try:
                    with urllib.request.urlopen(enroll_req) as enroll_res:
                        print("Enrollment successful")
                except urllib.error.HTTPError as e:
                    print(f"Enrollment Msg: {e.read().decode('utf-8')}")

    except Exception as e:
        print(f"Enrollment Error: {e}")
    
    # 3. Get My Courses
    courses_url = f"{BASE_URL}/api/classroom/courses/my"
    print(f"Fetching courses from: {courses_url}")
    
    req = urllib.request.Request(courses_url, headers={
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            print(f"Status Code: {status_code}")
            courses = json.loads(body)
            print(f"Found {len(courses)} courses")
            for c in courses:
                print(f" - [{c['code']}] {c['name']}")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_my_courses()
