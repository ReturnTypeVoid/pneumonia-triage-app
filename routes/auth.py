from flask import Blueprint, request, jsonify, redirect, url_for, render_template, make_response, flash, session
import requests, jwt, datetime, bcrypt
from db import get_user

auth = Blueprint('auth', __name__)

SECRET_KEY = "CvqDZUb7oEZmWDBUAKEbQoGF8rRJWzw4xG6ZpQ6Z9gNonDtdqyLwVM49RykZDrRT"
JWT_EXPIRY = 15  
REFRESH_EXPIRY = 1  

def generate_tokens(user_id, role, username, name):
    """
    Generate a new access and refresh token for a user.

    Description:
        Creates a short-lived access token and a longer-lived refresh token
        using the user's details. Tokens are signed using the app's secret key.

    Arguments:
        user_id (int): The user's ID.
        role (str): The user's role (e.g., admin, worker).
        username (str): The user's username.
        name (str): The user's name.

    Returns:
        Tuple: access_token (str), refresh_token (str)

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    access_token = jwt.encode({
        'user_id': user_id,
        'role': role,
        'username': username, 
        'name': name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRY)
    }, SECRET_KEY, algorithm='HS256')

    refresh_token = jwt.encode({
        'user_id': user_id,
        'username': username, 
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_EXPIRY)
    }, SECRET_KEY, algorithm='HS256')

    return access_token, refresh_token

def get_user_from_token():
    """
    Get user details from the access token in the cookie.

    Description:
        Checks if an access token exists in the cookies and decodes it to get
        user information. Handles expired or invalid tokens gracefully.

    Arguments:
        None

    Returns:
        dict or None: User data if the token is valid, otherwise None.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    token = request.cookies.get('access_token')
    if not token:
        return None
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return data  
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def clear_session(response):
    """
    Clear authentication cookies.

    Description:
        Wipes out the access and refresh tokens from the user's browser
        by setting their expiry to 0.

    Arguments:
        response (Response): A Flask response object to modify.

    Returns:
        Response: The same response with cleared cookies.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)  
    return response

def check_jwt_tokens():
    """
    Check access token and refresh if needed.

    Description:
        Looks for a valid access token in the cookies. If it's missing or expired,
        it tries to refresh it using the refresh token. If all else fails, it
        redirects to the login page and clears the session.

    Arguments:
        None

    Returns:
        Tuple: (user_data (dict or None), response (Response))

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    response = make_response()
    user_data = get_user_from_token()

    if not user_data:
        refresh_token = request.cookies.get('refresh_token')
        if refresh_token:
            refresh_response = requests.post(url_for('auth.refresh', _external=True), cookies=request.cookies)
            if refresh_response.status_code == 200:
                new_access_token = refresh_response.cookies.get('access_token')
                response.set_cookie('access_token', new_access_token)
                user_data = get_user_from_token()
            else:
                response = make_response(redirect(url_for('auth.login')))
                clear_session(response)
                return None, response
        else:
            response = make_response(redirect(url_for('auth.login')))
            clear_session(response)
            return None, response

    return user_data, response

def check_is_admin(user_data):
    """
    Check if the user is an admin.

    Description:
        Verifies that the user has the 'admin' role. If not, clears the session,
        flashes an error, and redirects to login.

    Arguments:
        user_data (dict): User info from the access token.

    Returns:
        Tuple: (bool, Response or None)

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    if not user_data or user_data['role'] != 'admin':
        response = make_response(redirect(url_for('auth.login')))
        clear_session(response)
        session.pop('_flashes', None)
        flash("You do not have permission to perform this action.", "error")
        return False, response

    return True, None

def check_is_worker(user_data):
    """
    Check if the user is a worker.

    Description:
        Confirms that the user has the 'worker' role. If not, clears the session
        and sends them to login.

    Arguments:
        user_data (dict): User info from the access token.

    Returns:
        Tuple: (bool, Response or None)

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    if not user_data or user_data['role'] != 'worker':
        response = make_response(redirect(url_for('auth.login')))
        clear_session(response)
        return False, response

    return True, None

def check_is_clinician(user_data):
    """
    Check if the user is a clinician.

    Description:
        Confirms that the user has the 'clinician' role. If not, clears the session
        and redirects them to login.

    Arguments:
        user_data (dict): User info from the access token.

    Returns:
        Tuple: (bool, Response or None)

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    if not user_data or user_data['role'] != 'clinician':
        response = make_response(redirect(url_for('auth.login')))
        clear_session(response)
        return False, response

    return True, None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route to handle user login.

    Description:
        Handles both showing the login form and processing login attempts.
        Verifies the user's credentials, sets access and refresh tokens on success,
        and redirects based on their role.

    Arguments:
        None

    Returns:
        Response: Login form or redirect based on login result.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  

        user = get_user(username)  

        if user and bcrypt.checkpw(password, user['password']):  
            access_token, refresh_token = generate_tokens(user['id'], user['role'], user['username'], user['name'])  

            if user['role'] == 'admin':
                response = make_response(redirect(url_for('users.list_users')))
            elif user['role'] == 'worker':
                response = make_response(redirect(url_for('patients.get_worker_patients')))
            else:
                response = make_response(redirect(url_for('patients.patients_reviewing')))

            response.set_cookie('access_token', access_token)
            response.set_cookie('refresh_token', refresh_token)
            return response
        
        session.pop('_flashes', None)
        flash("Invalid credentials. Please try again.", "error")
        return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth.route('/refresh', methods=['POST'])
def refresh():
    """
    Route to refresh the access token.

    Description:
        Checks the refresh token and issues a new access token if it's valid.
        Otherwise, clears the session and redirects to login.

    Arguments:
        None

    Returns:
        Response: New tokens or a redirect to login.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        session.pop('_flashes', None)
        flash("Invalid session!", "error")
        return redirect(url_for('auth.login'))

    try:
        data = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
        access_token, new_refresh_token = generate_tokens(data['user_id'], data.get('role'))

        response = jsonify({'message': 'Token refreshed'})
        response.set_cookie('access_token', access_token)
        response.set_cookie('refresh_token', new_refresh_token)
        return response

    except jwt.ExpiredSignatureError:
        session.pop('_flashes', None)
        flash("Session expired!", "error")
        return redirect(url_for('auth.login'))
    except jwt.InvalidTokenError:
        session.pop('_flashes', None)
        flash("Invalid session!", "error")
        return redirect(url_for('auth.login'))

@auth.route('/logout', methods=['POST'])
def logout():
    """
    Route to refresh the access token.

    Description:
        Checks the refresh token and issues a new access token if it's valid.
        Otherwise, clears the session and redirects to login.

    Arguments:
        None

    Returns:
        Response: New tokens or a redirect to login.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    response = make_response(redirect(url_for('auth.login')))
    clear_session(response)
    session.pop('_flashes', None)
    flash("Signed out!", "success")
    return response