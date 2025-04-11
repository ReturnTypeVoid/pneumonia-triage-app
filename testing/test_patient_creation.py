# testing/test_patient_creation.py
import pytest
import bcrypt
import time
from app import app
import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            try:
                worker_password = bcrypt.hashpw('HealthPass123!'.encode('utf-8'), bcrypt.gensalt())
                db.add_user("Test Worker", "test_worker", worker_password, "worker", "worker@example.com")
            except Exception as e:
                print(f"Setup error: {e}")
        
        yield client
        
        time.sleep(1)
        
        with app.app_context():
            try:
                conn = db.get_connection()
                conn.close()
                
                # Delete test patient if created
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE first_name = ? AND surname = ?", ("John", "Doe"))
                conn.commit()
                cursor.close()
                conn.close()
                
                time.sleep(1)
                
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", ("test_worker",))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Teardown error: {e}")

def test_patient_creation_validation(client):
    """Test patient record creation with validation"""
    response = client.post('/login', 
                         data={
                             'username': 'test_worker',
                             'password': 'HealthPass123!'
                         },
                         follow_redirects=True)
    assert response.status_code == 200
    
    response = client.get('/patients/new')
    assert response.status_code == 200
    assert b'<form' in response.data
    
   
    valid_data = {
        'first_name': 'John',
        'surname': 'Doe',
        'dob': '1978-05-15',  # Age 45
        'sex': 'Male',
        'email': 'johndoe@example.com',
        'phone': '555-123-4567',
        'fever': 'True',
        'cough': 'True',
        'worker_notes': 'Patient reports fatigue and loss of appetite',
        'address': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'zip': '12345',
        'height': '180',
        'weight': '80',
        'blood_type': 'O+',
        'smoker_status': 'Non-smoker',
        'alcohol_consumption': 'Occasional',
        'allergies': 'None',
        'vaccination_history': 'Up to date',
        'chest_pain': 'False',
        'shortness_of_breath': 'False',
        'fatigue': 'True',
        'chills_sweating': 'False',
        'cough_duration': '5',
        'cough_type': 'Dry'
    }
    
    response = client.post('/patients/new', 
                         data=valid_data,
                         follow_redirects=True)
    assert response.status_code == 200
    
    # Check for success indicators
    assert any([
        b'success' in response.data.lower(),
        b'added successfully' in response.data.lower(),
        b'Patient' in response.data and b'added' in response.data
    ])
    
    #  Navigate to patient list and verify
    response = client.get('/patients/')
    assert response.status_code == 200
    
    # Verify patient appears in list
    assert b'John' in response.data
    assert b'Doe' in response.data
    
    # Step 15: Verify patient record in database
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE first_name = ? AND surname = ?", ("John", "Doe"))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # Verify patient data was stored correctly
    assert patient is not None
    assert patient['first_name'] == 'John'
    assert patient['surname'] == 'Doe'
    assert patient['email'] == 'johndoe@example.com'
    assert patient['phone'] == '555-123-4567'
    assert patient['fever'] == 1  
    assert patient['cough'] == 1  