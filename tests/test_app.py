import pytest
import jwt
import datetime
from flask import url_for
from app import app, db
import bcrypt

# Setup for testing
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Setup test database
            db.create_all()
            
            # Create test users with different roles
            from db import execute_query
            
            # Worker user
            worker_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            execute_query(
                "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                ["worker", worker_password, "worker", "worker@example.com"]
            )
            
            # Admin user
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            execute_query(
                "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                ["admin", admin_password, "admin", "admin@example.com"]
            )
            
            # Clinician user
            clinician_password = bcrypt.hashpw('clinician123'.encode('utf-8'), bcrypt.gensalt())
            execute_query(
                "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                ["clinician", clinician_password, "clinician", "clinician@example.com"]
            )
            
        yield client
        
        # Teardown
        with app.app_context():
            db.drop_all()

def test_login_success(client):
    """Test successful login with valid credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'worker',
                             'password': 'password123'
                         },
                         follow_redirects=True)
    
    # Check if login was successful
    assert response.status_code == 200
    
    # Check if cookies were set
    cookies = [cookie.name for cookie in client.cookie_jar]
    assert 'access_token' in cookies
    assert 'refresh_token' in cookies

def test_login_failure(client):
    """Test login failure with invalid credentials"""
    response = client.post('/login', 
                         data={
                             'username': 'worker',
                             'password': 'wrongpassword'
                         },
                         follow_redirects=True)
    
    # Check if error message is shown
    assert response.status_code == 200
    assert b'Invalid Credentials' in response.data
    
    # Check that no cookies were set
    cookies = [cookie.name for cookie in client.cookie_jar]
    assert 'access_token' not in cookies or client.get_cookie('access_token').value == ''
    assert 'refresh_token' not in cookies or client.get_cookie('refresh_token').value == ''

def test_admin_access(client):
    """Test admin role can access admin routes"""
    # First login as admin
    client.post('/login', 
               data={
                   'username': 'admin',
                   'password': 'admin123'
               })
    
    # Try to access admin-only route (user management)
    response = client.get('/users')
    
    # Should be able to access
    assert response.status_code == 200
    assert b'User List' in response.data  # Assuming user list page has this text

def test_worker_restricted_access(client):
    """Test worker role cannot access admin routes"""
    # First login as worker
    client.post('/login', 
               data={
                   'username': 'worker',
                   'password': 'password123'
               })
    
    # Try to access admin-only route
    response = client.get('/users', follow_redirects=True)
    
    # Should be redirected to login (access denied)
    assert b'Login' in response.data

def test_clinician_access(client):
    """Test clinician role can access clinician routes"""
    # First login as clinician
    client.post('/login', 
               data={
                   'username': 'clinician',
                   'password': 'clinician123'
               })
    
    # Try to access clinician-only route (patient reviewing)
    response = client.get('/patients/reviewing')
    
    # Should be able to access
    assert response.status_code == 200
    assert b'Patients for Review' in response.data  # Assuming this text appears on the page