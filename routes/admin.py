from flask import Blueprint, request, render_template, redirect, url_for, make_response, session
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
