import bcrypt
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from routes.auth import check_jwt_tokens, check_is_admin, get_user_from_token
from db import check_user_exists, add_user, get_users, delete_user, update_user, get_user

users = Blueprint('users', __name__)

@users.route('/users', methods=['GET'])
def list_users():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    current_user = get_user_from_token()['username']
    return render_template('users/user_list.html', current_user=get_user(current_user), users=get_users())

@users.route('/users/create', methods=['GET', 'POST'])
def create_user():
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
            return render_template('users/user_form.html', current_user=get_user(current_user), error="Username already exists.")

        success = add_user(name, username, password, role, email)
        
        session.pop('_flashes', None)

        if success:
            flash("User added successfully.", "success")
        else:
            flash("Failed to add user.", "error")

        return redirect(url_for('users.list_users'))

    return render_template('users/user_form.html', current_user=get_user(current_user), user=None)

@users.route('/users/edit/<string:username>', methods=['GET', 'POST'])
def edit_user(username):
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
        password = request.form.get("password")
        role = request.form.get("role")
        email = request.form.get("email")

        
        if new_username != username and check_user_exists(new_username):
            return render_template('admin/user_form.html', 
                                   user=get_user(username), 
                                   current_user=get_user(current_user), 
                                   error="Username already exists.")

        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None

        
        if password:
            success = update_user(username=username, new_username=new_username, name=name, password=hashed_password, role=role, email=email)
        else:
            success = update_user(username=username, new_username=new_username, name=name, role=role, email=email)  

        session.pop('_flashes', None)

        if success:
            flash("User modified successfully.", "success")
        else:
            flash("Failed to modify user.", "error")
        return redirect(url_for('users.list_users'))

    return render_template('users/user_form.html', user=get_user(current_user), current_user=get_user(current_user))


@users.route('/users/delete/<string:username>', methods=['POST']) 
def delete_existing_user(username):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response
    
    success = delete_user(username)
    
    session.pop('_flashes', None)

    if success:
        flash("User deleted successfully.", "success")
    else:
        flash("Failed to delete user.", "error")
    return redirect(url_for('users.list_users'))