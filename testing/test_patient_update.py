# testing/test_patient_update.py

import pytest
import bcrypt
from app import app
import db
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            try:
                # Create worker user 
                worker_password = bcrypt.hashpw('HealthPass123!'.encode('utf-8'), bcrypt.gensalt())
                db.add_user("Test Health Worker", "test_health_worker", worker_password, "worker", "health@example.com")
                
                # Get worker ID
                worker_id = db.get_user_id("test_health_worker")
                
                # Create test patient
                db.add_patient(
                    first_name="Amna", 
                    surname="Test", 
                    address="123 Test St", 
                    city="Test City", 
                    state="Test State", 
                    zip="12345", 
                    dob="1967-10-25",  
                    sex="Female", 
                    height=165.0, 
                    weight=65.0, 
                    blood_type="A+", 
                    smoker_status="Non-smoker", 
                    alcohol_consumption="None", 
                    allergies="None", 
                    vaccination_history="Up to date", 
                    fever=1,  # Yes
                    cough=1,  # Yes
                    chest_pain=0,
                    shortness_of_breath=0,  # No
                    fatigue=0, 
                    chills_sweating=0, 
                    last_updated=datetime.now().strftime('%Y-%m-%d'), 
                    worker_id=worker_id,
                    email="amna@example.com",
                    phone="123-456-7890",
                    cough_duration=5,
                    cough_type="Dry"
                )
            except Exception as e:
                print(f"Setup error: {e}")
                connection = db.get_connection()
                connection.close()
                raise
        
        yield client
        
        with app.app_context():
            try:
                connection = db.get_connection()
                connection.close()
                
                connection = db.get_connection()
                cursor = connection.cursor()
                
                cursor.execute("DELETE FROM patients WHERE email = ?", ("amna@example.com",))
                
                cursor.execute("DELETE FROM users WHERE username = ?", ("test_health_worker",))
                
                connection.commit()
                cursor.close()
                connection.close()
            except Exception as e:
                print(f"Teardown error: {e}")

def get_test_patient_id(email):
    """Helper function to get the ID of a test patient by email"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM patients WHERE email = ?", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting patient ID: {e}")
        return None

def test_patient_record_update(client):
    """Test the functionality to update patient records"""
    response = client.post('/login', 
                         data={
                             'username': 'test_health_worker',
                             'password': 'HealthPass123!'
                         },
                         follow_redirects=True)
    
    # Verify login success
    assert response.status_code == 200
    
    response = client.get('/patients/')
    assert response.status_code == 200
    
    patient_id = get_test_patient_id("amna@example.com")
    assert patient_id is not None, "Could not find test patient"
    
    #Go to the patient edit page
    response = client.get(f'/patients/edit/{patient_id}')
    assert response.status_code == 200
    assert b'Amna' in response.data
    
#    Update the patient record with new data
    updated_data = {
        'first_name': 'Amna',
        'surname': 'Test',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'Test State',
        'zip': '12345',
        'dob': '2001-10-25',  # Updated DOB
        'sex': 'Female',
        'height': '165.0',
        'weight': '65.0',
        'blood_type': 'A+',
        'smoker_status': 'Non-smoker',
        'alcohol_consumption': 'None',
        'allergies': 'None',
        'vaccination_history': 'Up to date',
        'fever': 'False',  # Updated to No
        'cough': 'False',  # Updated to No
        'chest_pain': 'False',
        'shortness_of_breath': 'True',  # Updated to Yes
        'fatigue': 'False',
        'chills_sweating': 'False',
        'email': 'amna@example.com',
        'phone': '123-456-7890',
        'cough_duration': '0',  # Updated cough to No
        'cough_type': 'None',   # Updated cough to No
        'worker_notes': 'Updated patient record for testing'
    }
    
    response = client.post(
        f'/patients/edit/{patient_id}',
        data=updated_data,
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Check for success message 
    
    # Go back to the dashboard and verify the changes
    response = client.get('/patients/')
    assert response.status_code == 200
    
    # go to patient edit page again to verify changes
    response = client.get(f'/patients/edit/{patient_id}')
    assert response.status_code == 200
    
    assert b'2001-10-25' in response.data  # Check updated DOB
    
    updated_patient = db.get_patient(patient_id)
    assert updated_patient is not None
    
    assert updated_patient['dob'] == '2001-10-25'
    assert updated_patient['fever'] == 0  # No
    assert updated_patient['cough'] == 0  # No
    assert updated_patient['shortness_of_breath'] == 1  # Yes
    assert updated_patient['cough_duration'] == 0
    assert updated_patient['cough_type'] == 'None'
    
    dob = datetime.strptime(updated_patient['dob'], '%Y-%m-%d')
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    assert 19 <= age <= 23, f"Expected age around 20, got {age}"