# tests/test_auth.py
import pytest
import bcrypt
from app import app
import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # creating test users with hasshed password
        with app.app_context():
            # worker user
            worker_password = bcrypt.hashpw('HealthPass123!'.encode('utf-8'), bcrypt.gensalt())
            db.add_user("Test Health Worker", "test_health_worker", worker_password, "worker", "health@example.com")
            
            #  admin user
            admin_password = bcrypt.hashpw('AdminPass123!'.encode('utf-8'), bcrypt.gensalt())
            db.add_user("Test Admin", "test_admin", admin_password, "admin", "admin@example.com")
            
            #  clinician user
            clinician_password = bcrypt.hashpw('ClinicPass123!'.encode('utf-8'), bcrypt.gensalt())
            db.add_user("Test Clinician", "test_clinician", clinician_password, "clinician", "clinician@example.com")
        
        yield client
        
        with app.app_context():
            db.delete_user("test_health_worker")
            db.delete_user("test_admin")
            db.delete_user("test_clinician")

def test_login_page_loads(client):
    """Test that the login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_health_worker_login(client):
    """Test login with health worker credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'test_health_worker',
                             'password': 'HealthPass123!'
                         },
                         follow_redirects=True)
    
    assert response.status_code == 200
    
    assert client.get_cookie('access_token') is not None
    
    assert b'Invalid credentials' not in response.data
    
    assert any([
        b'Patients' in response.data,
        b'X-ray Upload' in response.data,
        b'Patient Management' in response.data
    ])
    
    # this check if admin features are not accessible
    assert b'User Management' not in response.data

def test_clinician_login(client):
    """Test login with clinician credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'test_clinician',
                             'password': 'ClinicPass123!'
                         },
                         follow_redirects=True)
    
    # this check if login was successful
    assert response.status_code == 200
    
    # this check for access token cookie
    assert client.get_cookie('access_token') is not None
    
    # this check for clinician specific content
    assert b'Invalid credentials' not in response.data
    
    assert any([
        b'Case Review' in response.data,
        b'Patients' in response.data,
        b'Recommendations' in response.data,
        b'reviewing' in response.data.lower()
    ])
    
    # this check that admin features are not accessible
    assert b'User Management' not in response.data

def test_admin_login(client):
    """Test login with admin credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'test_admin',
                             'password': 'AdminPass123!'
                         },
                         follow_redirects=True)
    
    # This check if login was successful
    assert response.status_code == 200
    
    # This check for access token cookie
    assert client.get_cookie('access_token') is not None
    
    # This check for admin specific content
    assert b'Invalid credentials' not in response.data
    
    assert any([
        b'User Management' in response.data,
        b'Users' in response.data,
        b'System Settings' in response.data
    ])

def test_login_failure(client):
    """Test login failure with invalid credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'test_health_worker',
                             'password': 'WrongPassword123!'
                         },
                         follow_redirects=True)
    
    # Check if error message is shown 
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data
    
    # Ensure we don't have an access token
    assert client.get_cookie('access_token') is None

def test_worker_restricted_access(client):
    """Test health worker role cannot access admin routes"""
    # First login as worker
    client.post('/login', 
               data={
                   'username': 'test_health_worker',
                   'password': 'HealthPass123!'
               })
    
    # Try to access admin-only route
    response = client.get('/users', follow_redirects=True)
    
    # Should be redirected with an error message
    assert response.status_code == 200
    assert any([
        b'You do not have permission' in response.data,
        b'Access Denied' in response.data,
        b'Login' in response.data
    ])

def test_clinician_restricted_access(client):
    """Test clinician role cannot access admin routes"""
    # First login as clinician
    client.post('/login', 
               data={
                   'username': 'test_clinician',
                   'password': 'ClinicPass123!'
               })
    
    # Try to access admin-only route
    response = client.get('/users', follow_redirects=True)
    
    # Should be redirected with an error message
    assert response.status_code == 200
    assert any([
        b'You do not have permission' in response.data,
        b'Access Denied' in response.data,
        b'Login' in response.data
    ])

def test_logout(client):
    """Test that users can log out successfully"""
    # First login
    client.post('/login', data={
        'username': 'test_health_worker',
        'password': 'HealthPass123!'
    }, follow_redirects=True)
    
    assert client.get_cookie('access_token') is not None
    
    response = client.post('/logout', follow_redirects=True)
    
    # Check response
    assert response.status_code == 200
    assert b'Signed out!' in response.data
    
    assert client.get_cookie('access_token') is None or client.get_cookie('access_token').value == ''