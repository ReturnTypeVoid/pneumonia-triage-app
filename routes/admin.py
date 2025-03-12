from flask import Blueprint, request, render_template, redirect, url_for, flash
import bcrypt
from routes.auth import check_jwt_tokens, check_is_admin, get_user_from_token
from db import check_user_exists, add_user, get_users, delete_user, update_user, get_user, get_settings, update_twilio_settings, update_smtp_settings

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
        password = request.form.get("password")
        role = request.form.get("role")
        email = request.form.get("email")

        # Ensure new username is unique
        if new_username != username and check_user_exists(new_username):
            return render_template('admin/user_form.html', 
                                   user=get_user(username), 
                                   current_user=get_user(current_user), 
                                   error="Username already exists.")

        # Only hash and update password if it's provided
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None

        # Update user details, but only pass password if it was provided
        if password:
            update_user(username=username, new_username=new_username, name=name, password=hashed_password, role=role, email=email)
        else:
            update_user(username=username, new_username=new_username, name=name, role=role, email=email)  # No password update

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/user_form.html', user=get_user(username), current_user=get_user(current_user))


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

@admin.route('/admin/settings/', methods=['GET'])
def edit_settings():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response
    
    current_user = get_user_from_token()['username']

    settings = get_settings()

    return render_template('admin/settings.html', current_user=get_user(current_user), settings=settings)

@admin.route('/admin/settings/update_twilio', methods=['POST'])
def update_twilio():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    # Get form data
    twilio_account_id = request.form.get('twilio_account_id')
    twilio_secret_key = request.form.get('twilio_secret_key')
    twilio_phone = request.form.get('twilio_phone')

    # Update in database
    update_twilio_settings(twilio_account_id, twilio_secret_key, twilio_phone)

    return redirect(url_for('admin.edit_settings'))

@admin.route('/admin/settings/update_smtp', methods=['POST'])
def update_smtp():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    # Get form data
    smtp_server = request.form.get('smtp_server')
    smtp_port = request.form.get('smtp_port')
    smtp_tls = request.form.get('smtp_tls') == 'on'  # Convert checkbox to boolean
    smtp_username = request.form.get('smtp_username')
    smtp_password = request.form.get('smtp_password')
    smtp_sender = request.form.get('smtp_sender')

    # Update in database
    update_smtp_settings(smtp_server, smtp_port, smtp_tls, smtp_username, smtp_password, smtp_sender)

    return redirect(url_for('admin.edit_settings'))