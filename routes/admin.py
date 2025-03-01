from flask import Blueprint, request, render_template, redirect, url_for, make_response
import bcrypt
import requests
from routes.auth import get_user_from_token, clear_session 
from db import get_db_connection

admin = Blueprint('admin', __name__)

def list_users():
    # Connect to the database
    conn = get_db_connection()
    c = conn.cursor()

    # sql query, storing the returned data in users var - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT
    c.execute('SELECT id, username, role FROM users')
    users = c.fetchall()  

    conn.close()  # Close the database connection - Should ALWAYS close when finished - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT

    return users

def user_exists(username):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = c.fetchone()  # Will return None if no user is found
        return result is not None  # Returns True if user exists, otherwise False
    except Exception as e:
        print(f"Error checking user")
        return False
    finally:
        conn.close()


def add_user(name, username, password, role, email):
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
INSERT INTO users (name, username, password, role, email)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(username) DO NOTHING
''', (name, username, password, role, email))
    
    conn.commit()
    conn.close()


@admin.route('/admin/dashboard')
def dashboard():
    response = make_response()
    user_data = get_user_from_token()

    if not user_data or user_data['role'] != 'admin':
        response = make_response(redirect(url_for('auth.login')))
        clear_session(response)
        return response

    # refresh token if it's expired
    refresh_token = request.cookies.get('refresh_token')
    if not user_data and refresh_token:
        refresh_response = requests.post(url_for('auth.refresh', _external=True), cookies=request.cookies)
        if refresh_response.status_code == 200:
            new_access_token = refresh_response.cookies.get('access_token')
            response.set_cookie('access_token', new_access_token, httponly=True, secure=True)
            user_data = get_user_from_token()
        else:
            response = make_response(redirect(url_for('auth.login')))
            clear_session(response)
            return response
    
    return render_template('admin/dashboard.html', users=list_users())


@admin.route('/admin/user/create', methods=['POST'])
def add_new_user():
    response = make_response()
    user_data = get_user_from_token()

    if not user_data or user_data['role'] != 'admin':
        response = make_response(redirect(url_for('auth.login')))
        clear_session(response)
        return response
    
    refresh_token = request.cookies.get('refresh_token')
    if not user_data and refresh_token:
        refresh_response = requests.post(url_for('auth.refresh', _external=True), cookies=request.cookies)
        if refresh_response.status_code == 200:
            new_access_token = refresh_response.cookies.get('access_token')
            response.set_cookie('access_token', new_access_token, httponly=True, secure=True)
            user_data = get_user_from_token()
        else:
            response = make_response(redirect(url_for('auth.login')))
            clear_session(response)
            return response
    
    name = request.form.get('name')
    username = request.form.get('username')
    password = bcrypt.hashpw((request.form.get('password')).encode('utf-8'), bcrypt.gensalt())
    role = request.form.get('role')
    email = request.form.get('email')

    if user_exists(username):
        return render_template('admin/dashboard.html', error="Username already exists.", users=list_users())

    add_user(name, username, password, role, email)

    return render_template('admin/dashboard.html', users=list_users())

