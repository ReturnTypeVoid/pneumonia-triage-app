# # tests/test_auth.py
# import pytest
# from app import app

# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     app.config['WTF_CSRF_ENABLED'] = False
#     with app.test_client() as client:
#         yield client

# def test_login_page_loads(client):
#     """Test that the login page loads correctly"""
#     response = client.get('/login')
#     assert response.status_code == 200
#     # Check that the page contains login form elements
#     assert b'Login' in response.data or b'username' in response.data or b'password' in response.data

# def test_login_with_invalid_credentials(client):
#     """Test login with invalid credentials"""
#     response = client.post('/login', 
#                          data={
#                              'username': 'nonexistentuser',
#                              'password': 'wrongpassword'
#                          },
#                          follow_redirects=True)
    
#     assert response.status_code == 200
#     # Check for error message (adjust based on your actual error message)
#     assert b'Invalid' in response.data or b'failed' in response.data or b'incorrect' in response.dataa


# tests/test_app.py
import pytest
import bcrypt
from app import app
import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # Setup - create test users
        with app.app_context():
            # Create worker user with hashed password
            worker_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            db.add_user("Test Worker", "test_worker", worker_password, "worker", "worker@example.com")
            
            # Create admin user
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            db.add_user("Test Admin", "test_admin", admin_password, "admin", "admin@example.com")
            
            # Create clinician user
            clinician_password = bcrypt.hashpw('clinician123'.encode('utf-8'), bcrypt.gensalt())
            db.add_user("Test Clinician", "test_clinician", clinician_password, "clinician", "clinician@example.com")
        
        yield client
        
        # Teardown - clean up test users
        with app.app_context():
            db.delete_user("test_worker")
            db.delete_user("test_admin")
            db.delete_user("test_clinician")

def test_login_success(client):
    """Test successful login with valid credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'test_worker',
                             'password': 'password123'
                         },
                         follow_redirects=True)
    
    # Check if login was successful
    assert response.status_code == 200
    
    # Check response content for indicators of successful login
    # These assertions should be adjusted based on what actually appears in your application
    assert b'Invalid Credentials' not in response.data
    assert any([
        b'Logout' in response.data,
        b'Dashboard' in response.data,
        b'Patients' in response.data,
        b'Welcome' in response.data
    ])

def test_login_failure(client):
    """Test login failure with invalid credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'test_worker',
                             'password': 'wrongpassword'
                         },
                         follow_redirects=True)
    
    # Check if error message is shown
    assert response.status_code == 200
    assert b'Invalid Credentials' in response.data

def test_admin_access(client):
    """Test admin role can access admin routes"""
    # First login as admin
    client.post('/login', 
               data={
                   'username': 'test_admin',
                   'password': 'admin123'
               })
    
    # Try to access admin-only route (user management)
    response = client.get('/users')
    
    # Should be able to access
    assert response.status_code == 200
    # Look for elements that would be on the user list page
    assert b'User List' in response.data or b'Users' in response.data or b'test_admin' in response.data

def test_worker_restricted_access(client):
    """Test worker role cannot access admin routes"""
    # First login as worker
    client.post('/login', 
               data={
                   'username': 'test_worker',
                   'password': 'password123'
               })
    
    # Try to access admin-only route
    response = client.get('/users', follow_redirects=True)
    
    # Should be redirected to login (access denied)
    assert b'Login' in response.data or response.status_code == 403

def test_clinician_access(client):
    """Test clinician role can access clinician routes"""
    # First login as clinician
    client.post('/login', 
               data={
                   'username': 'test_clinician',
                   'password': 'clinician123'
               })
    
    # Try to access clinician-only route (patient reviewing)
    response = client.get('/patients/reviewing')
    
    # Should be able to access
    assert response.status_code == 200
    # Look for elements that would be on the patient reviewing page
    assert b'Patients' in response.data or b'Review' in response.data