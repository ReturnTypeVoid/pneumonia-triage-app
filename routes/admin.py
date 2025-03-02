from flask import Blueprint, request, render_template, redirect, url_for, make_response
import bcrypt
import requests
from routes.auth import get_user_from_token, clear_session 
from db import check_user_exists, add_user, list_users

admin = Blueprint('admin', __name__)

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

    if check_user_exists(username):
        return render_template('admin/dashboard.html', error="Username already exists.", users=list_users())

    add_user(name, username, password, role, email)

    return render_template('admin/dashboard.html', users=list_users())

