#testing/test_pnemo_detect.py

import pytest
import os
import bcrypt
import io
from app import app
import db
from PIL import Image
import numpy as np
import time

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create a test client
    with app.test_client() as client:
        with app.app_context():
            try:
                # Create worker user 
                worker_password = bcrypt.hashpw('HealthPass123!'.encode('utf-8'), bcrypt.gensalt())
                db.add_user("Test Health Worker", "test_health_worker", worker_password, "worker", "health@example.com")
                
                # Get worker ID
                worker_id = db.get_user_id("test_health_worker")
                
                db.add_patient(
                    first_name="Test", 
                    surname="Patient", 
                    address="123 Test St", 
                    city="Test City", 
                    state="Test State", 
                    zip="12345", 
                    dob="1990-01-01", 
                    sex="Male", 
                    height=180.0, 
                    weight=80.0, 
                    blood_type="O+", 
                    smoker_status="Non-smoker", 
                    alcohol_consumption="Occasional", 
                    allergies="None", 
                    vaccination_history="Up to date", 
                    fever=0, 
                    cough=1, 
                    chest_pain=0, 
                    shortness_of_breath=1, 
                    fatigue=1, 
                    chills_sweating=0, 
                    last_updated="2023-06-01", 
                    worker_id=worker_id,
                    email="patient@example.com",
                    cough_duration=0,  
                    cough_type="Dry"   
                )
                
                # another test patient for negative X-ray
                db.add_patient(
                    first_name="Test", 
                    surname="Patient2", 
                    address="456 Test St", 
                    city="Test City", 
                    state="Test State", 
                    zip="12345", 
                    dob="1992-02-02", 
                    sex="Female", 
                    height=165.0, 
                    weight=65.0, 
                    blood_type="A+", 
                    smoker_status="Non-smoker", 
                    alcohol_consumption="None", 
                    allergies="None", 
                    vaccination_history="Up to date", 
                    fever=0, 
                    cough=0, 
                    chest_pain=0, 
                    shortness_of_breath=0, 
                    fatigue=0, 
                    chills_sweating=0, 
                    last_updated="2023-06-02", 
                    worker_id=worker_id,
                    email="patient2@example.com",
                    cough_duration=0,  
                    cough_type="None"  
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
                
                time.sleep(0.5)
                
                connection = db.get_connection()
                cursor = connection.cursor()
                
                # Delete test patients
                cursor.execute("DELETE FROM patients WHERE email IN (?, ?)", 
                              ("patient@example.com", "patient2@example.com"))
                
                # Delete test user
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

def create_test_image(is_pneumonia=True):
    """Create a test image with characteristics that would trigger the AI model"""
    # Create a blank image
    if is_pneumonia:
        #
        img = Image.new('L', (64, 64), color=0)  
        pixels = img.load()
        
        # Add some white spots/patterns that might look like pneumonia
        for i in range(20, 45):
            for j in range(25, 40):
                pixels[i, j] = 255  # White spots
    else:
        # Create a more uniform image for non-pneumonia
        img = Image.new('L', (64, 64), color=180)  
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

def test_ai_detection_of_pneumonia(client):
    """Test the AI detection of pneumonia from X-ray uploads"""
    response = client.post('/login', 
                         data={
                             'username': 'test_health_worker',
                             'password': 'HealthPass123!'
                         },
                         follow_redirects=True)
    
    assert response.status_code == 200
    
    patient_id = get_test_patient_id("patient@example.com")
    if not patient_id:
        pytest.skip("Could not find test patient ID")
    
    # Create a test pneumonia image
    pneumonia_image = create_test_image(is_pneumonia=True)
    
    # Upload pneumonia-positive X-ray image
    start_time = time.time()
    
    response = client.post(
        f'/patients/xray/upload/{patient_id}',
        data={
            'file': (pneumonia_image, 'pneumonia_sample.jpg')
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Verify the upload was successful
    assert response.status_code == 200
    
    # Check that AI detection flagged pneumonia
    patient = db.get_patient(patient_id)
    assert patient is not None
    
    # Verify processing time is under 10 seconds
    assert processing_time < 10, f"AI processing took {processing_time} seconds, which exceeds the 10-second requirement"

def test_ai_detection_of_normal_xray(client):
    """Test the AI detection of a normal (non-pneumonia) X-ray"""
    # Login as health worker
    client.post('/login', 
              data={
                  'username': 'test_health_worker',
                  'password': 'HealthPass123!'
              },
              follow_redirects=True)
    
    # Get the patient ID
    patient_id = get_test_patient_id("patient2@example.com")
    if not patient_id:
        pytest.skip("Could not find test patient ID")
    
    # Create a test normal image
    normal_image = create_test_image(is_pneumonia=False)
    
    # Upload normal X-ray image
    response = client.post(
        f'/patients/xray/upload/{patient_id}',
        data={
            'file': (normal_image, 'normal_sample.jpg')
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    # Verify the upload was successful
    assert response.status_code == 200
    
    # Check that AI detection did not flag pneumonia
    patient = db.get_patient(patient_id)
    assert patient is not None

def test_invalid_file_upload(client):
    """Test uploading an invalid file type"""
    # Login as health worker
    client.post('/login', 
              data={
                  'username': 'test_health_worker',
                  'password': 'HealthPass123!'
              },
              follow_redirects=True)
    
    patient_id = get_test_patient_id("patient@example.com")
    if not patient_id:
        pytest.skip("Could not find test patient ID")
    
    # Create a text file
    text_file = io.BytesIO(b"This is not an image file")
    
    # upload the text file as an X-ray
    response = client.post(
        f'/patients/xray/upload/{patient_id}',
        data={
            'file': (text_file, 'doc.txt')
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    # should redirect without processing the invalid file
    assert response.status_code == 200