import sys
from datetime import datetime
sys.path.insert(0, r'D:\RPS_rough\RPS_School_Roh')
from fastapi.testclient import TestClient
from app.main import app

def get_unique_inquiry_payload(suffix=""):
    if not suffix:
        suffix = datetime.now().strftime('%s%f')[5:12]
    return {
        'first_name': f'Aarav{suffix}',
        'middle_name': 'Kumar',
        'last_name': f'Sharma{suffix}',
        'gender': 'male',
        'father_name': f'Rohit{suffix}',
        'dob': '2018-04-10',
        'student_mobile': f'+9199999{suffix}',
        'parent_mobile': f'+9112345{suffix}',
        'email': f'parent{suffix}@example.com',
        'address': '123 School Road, City',
        'last_school': 'ABC Public School',
        'current_class': 'Grade 4',
        'admission_for_class': 'Grade 5',
        'last_school_percentage': 85.5,
    }

client = TestClient(app)
payload = get_unique_inquiry_payload('001')
resp = client.post('/api/v1/public/student/inquiry', json=payload)
print(resp.status_code)
print(resp.json())
