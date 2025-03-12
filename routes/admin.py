from flask import Blueprint, request, render_template, redirect, url_for
import bcrypt
from routes.auth import check_jwt_tokens, check_is_admin, get_user_from_token
from db import check_user_exists, add_user, get_users, delete_user, update_user, get_user

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
def dashboard():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    current_user = get_user_from_token()['username']
    
    return render_template('admin/user_list.html', current_user=get_user(current_user), users=get_users())

@admin.route('/admin/user/list')
def user_list():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    current_user = get_user_from_token()['username']

    return render_template('admin/user_list.html', current_user=get_user(current_user), users=get_users())

@admin.route('/admin/user/create', methods=['GET', 'POST'])
def add_new_user():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    current_user = get_user_from_token()['username']

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
        role = request.form.get('role')
        email = request.form.get('email')

        if check_user_exists(username):
            return render_template('admin/user_form.html', current_user=get_user(current_user), error="Username already exists.")

        add_user(name, username, password, role, email)

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/user_form.html', current_user=get_user(current_user), user=None)

@admin.route('/admin/user/edit/<username>', methods=['GET', 'POST'])
def edit_existing_user(username):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    current_user = get_user_from_token()['username']

    if request.method == 'POST':
        new_username = request.form.get("username")
        name = request.form.get("name")
        password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
        role = request.form.get("role")
        email = request.form.get("email")

        if new_username != username and check_user_exists(new_username):
            return render_template('admin/user_form.html', 
                                   user=get_user(username), 
                                   current_user=get_user(current_user), 
                                   error="Username already exists.")

        update_user(username=username, new_username=new_username, name=name, password=password, role=role, email=email)

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/user_form.html', 
                           user=get_user(username), 
                           current_user=get_user(current_user))

@admin.route('/admin/user/delete/<username>', methods=['POST'])
def delete_existing_user(username):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response
    
    delete_user(username)
    
    return redirect(url_for('admin.dashboard'))

@admin.route('/admin/settings/edit', methods=['GET', 'POST'])
def edit_settings():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response
    
    current_user = get_user_from_token()['username']

    return render_template('admin/settings.html', current_user=get_user(current_user))
