from flask import Blueprint, request, jsonify, redirect, url_for, render_template, make_response
import jwt
import datetime
import bcrypt
import os
from db import get_db_connection

SECRET_KEY = "CvqDZUb7oEZmWDBUAKEbQoGF8rRJWzw4xG6ZpQ6Z9gNonDtdqyLwVM49RykZDrRT"
JWT_EXPIRY = 15  # 15 min access token
REFRESH_EXPIRY = 1  # 1 day refresh token - used to validate the access token and refresh it without logging the user out

auth = Blueprint('auth', __name__)

def generate_tokens(user_id, role):
    access_token = jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRY)
    }, SECRET_KEY, algorithm='HS256')

    refresh_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_EXPIRY)
    }, SECRET_KEY, algorithm='HS256')

    return access_token, refresh_token

def get_user_from_token():
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
    response.set_cookie('access_token', '', expires=0, httponly=True, secure=True)
    response.set_cookie('refresh_token', '', expires=0, httponly=True, secure=True)  # clears both tokens
    return response

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            access_token, refresh_token = generate_tokens(user['id'], user['role'])

            if user['role'] == 'admin':
                response = make_response(redirect(url_for('admin.dashboard')))
            elif user['role'] == 'worker':
                response = make_response(redirect(url_for('worker.dashboard')))
            else:
                response = make_response(redirect(url_for('clinician.dashboard')))

            response.set_cookie('access_token', access_token, httponly=True, secure=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
            return response

        return render_template('login.html', error='Invalid Credentials')

    return render_template('login.html')

@auth.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        return jsonify({'error': 'Missing refresh token'}), 401

    try:
        data = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
        access_token, new_refresh_token = generate_tokens(data['user_id'], data.get('role'))

        response = jsonify({'message': 'Token refreshed'})
        response.set_cookie('access_token', access_token, httponly=True, secure=True)
        response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True)
        return response

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token expired, please log in again'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401

@auth.route('/logout', methods=['POST'])
def logout():
    response = make_response(redirect(url_for('auth.login')))
    clear_session(response)
    return response