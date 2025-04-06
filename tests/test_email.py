#this is using the patients data available in database

import pytest
from unittest.mock import patch, MagicMock
from app import app
from db import list_patients  # Import the function that returns all patients

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # Login as a worker user
        client.post('/login', 
                   data={
                       'username': 'worker',  # Use an existing worker account
                       'password': 'worker123'
                   })
        yield client

@pytest.mark.integration
def test_send_email_to_real_patient(client):
    """Test sending an email to a real patient in the database"""
    # Find a patient with a valid email
    with app.app_context():
        all_patients = list_patients("")  # Empty search returns all patients
        patient_with_email = None
        
        for patient in all_patients:
            # Access sqlite3.Row objects using index notation
            if patient['email'] and '@' in patient['email']:
                patient_with_email = patient
                break
        
        if not patient_with_email:
            pytest.skip("No patients with valid email found in database")
    
    # Patch only the SMTP part to avoid sending real emails
    with patch('smtplib.SMTP') as mock_smtp:
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Send notification to the real patient
        response = client.post(f'/send-email/{patient_with_email["id"]}')
        
        # Check response
        assert response.status_code == 200
        
        # Verify email was attempted with correct address
        mock_smtp_instance.sendmail.assert_called_once()
        call_args = mock_smtp_instance.sendmail.call_args[0]
        assert patient_with_email['email'] in call_args[1]

@pytest.mark.integration
def test_email_behavior_with_real_empty_address(client):
    """Test behavior with a real patient having empty email"""
    # Find a patient with an empty email
    with app.app_context():
        all_patients = list_patients("")  # Empty search returns all patients
        patient_without_email = None
        
        for patient in all_patients:
            # Access sqlite3.Row objects using index notation
            if not patient['email'] or patient['email'] == '':
                patient_without_email = patient
                break
        
        if not patient_without_email:
            pytest.skip("No patients with empty email found in database")
    
    # Patch only the SMTP part
    with patch('smtplib.SMTP') as mock_smtp:
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Send notification to the real patient
        response = client.post(f'/send-email/{patient_without_email["id"]}')
        
        # Document behavior with real empty email
        assert response.status_code == 200
        mock_smtp_instance.sendmail.assert_called_once()
        call_args = mock_smtp_instance.sendmail.call_args[0]
        assert call_args[1] == ''



############################################################

#this is a mock-up coding for email:



# import pytest
# from unittest.mock import patch, MagicMock
# from app import app
# import json

# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     app.config['WTF_CSRF_ENABLED'] = False
    
#     with app.test_client() as client:
#         yield client

# @patch('routes.utilities.get_patient')
# @patch('routes.utilities.get_settings')
# @patch('routes.utilities.get_user')
# @patch('routes.utilities.get_user_from_token')
# @patch('routes.utilities.check_jwt_tokens')
# @patch('smtplib.SMTP')
# def test_send_email_success(mock_smtp, mock_check_jwt, mock_get_user_from_token, 
#                            mock_get_user, mock_get_settings, mock_get_patient, client):
#     """Test successful email notification when patient has valid email"""
#     # Mock JWT authentication
#     mock_check_jwt.return_value = ({"username": "test_worker", "role": "worker"}, None)
    
#     # Mock user token retrieval
#     mock_get_user_from_token.return_value = {"username": "test_worker"}
    
#     # Mock patient data with valid email
#     mock_get_patient.return_value = {
#         "id": 1,
#         "first_name": "John",
#         "surname": "Doe",
#         "email": "patient@example.com",  # Valid email
#         "case_closed": True  # Case is closed as per user story
#     }
    
#     # Mock worker data
#     mock_get_user.return_value = {
#         "name": "Test Worker",
#         "username": "test_worker",
#         "role": "worker"
#     }
    
#     # Mock SMTP settings
#     mock_get_settings.return_value = {
#         "smtp_server": "smtp.example.com",
#         "smtp_port": 587,
#         "smtp_tls": True,
#         "smtp_username": "test@example.com",
#         "smtp_password": "password",
#         "smtp_sender": "noreply@example.com"
#     }
    
#     # Mock SMTP instance
#     mock_smtp_instance = MagicMock()
#     mock_smtp.return_value = mock_smtp_instance
    
#     # Send email notification
#     response = client.post('/send-email/1')
    
#     # Check response
#     assert response.status_code == 200
    
#     # Verify SMTP was used correctly
#     mock_smtp.assert_called_once_with("smtp.example.com", 587)
#     mock_smtp_instance.starttls.assert_called_once()
#     mock_smtp_instance.login.assert_called_once()
#     mock_smtp_instance.sendmail.assert_called_once()
    
#     # Verify email was sent to the correct address
#     call_args = mock_smtp_instance.sendmail.call_args[0]
#     assert "patient@example.com" in call_args[1]  # The recipient should be the patient's email
    
#     mock_smtp_instance.quit.assert_called_once()

# @patch('routes.utilities.get_patient')
# @patch('routes.utilities.get_settings')
# @patch('routes.utilities.get_user')
# @patch('routes.utilities.get_user_from_token')
# @patch('routes.utilities.check_jwt_tokens')
# @patch('smtplib.SMTP')
# def test_email_behavior_with_empty_address(mock_smtp, mock_check_jwt, mock_get_user_from_token,
#                                  mock_get_user, mock_get_settings, mock_get_patient, client):
#     """Test system behavior when patient has empty email address"""
#     # Mock JWT authentication
#     mock_check_jwt.return_value = ({"username": "test_worker", "role": "worker"}, None)
    
#     # Mock user token retrieval
#     mock_get_user_from_token.return_value = {"username": "test_worker"}
    
#     # Mock patient data with empty email
#     mock_get_patient.return_value = {
#         "id": 2,
#         "first_name": "Jane",
#         "surname": "Smith",
#         "email": "",  # Empty email
#         "case_closed": True  # Case is closed as per user story
#     }
    
#     # Mock worker data
#     mock_get_user.return_value = {
#         "name": "Test Worker",
#         "username": "test_worker",
#         "role": "worker"
#     }
    
#     # Mock SMTP settings
#     mock_get_settings.return_value = {
#         "smtp_server": "smtp.example.com",
#         "smtp_port": 587,
#         "smtp_tls": True,
#         "smtp_username": "test@example.com",
#         "smtp_password": "password",
#         "smtp_sender": "noreply@example.com"
#     }
    
#     # Mock SMTP instance
#     mock_smtp_instance = MagicMock()
#     mock_smtp.return_value = mock_smtp_instance
    
#     # Try to send notification
#     response = client.post('/send-email/2')
    
#     #  The application attempts to send an email even with an empty recipient address and returns a 200 status code
#     assert response.status_code == 200
#     mock_smtp_instance.sendmail.assert_called_once()
    
#     # Verify that the empty email address is used in the sendmail call
#     call_args = mock_smtp_instance.sendmail.call_args[0]
#     assert call_args[1] == ""  # The recipient is an empty string
    
 