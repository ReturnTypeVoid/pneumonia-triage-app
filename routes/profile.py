from flask import Blueprint, render_template, redirect, url_for, request
from routes.auth import check_jwt_tokens, get_user_from_token, check_is_worker, check_is_clinician
from db import get_user, check_user_exists, update_user
import bcrypt


profile = Blueprint('profile', __name__)

@profile.route('/profile/view', methods=['GET'])
def view_worker():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response
    
    current_user = get_user_from_token()['username']

    return render_template('worker/profile/form.html', current_user=get_user(current_user), user=get_user(current_user))




@profile.route('/profile/update', methods=['POST'])
def update_worker_profile():
    # Authenticate user
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response  # Return response if authentication fails

    # Ensure the user is either a worker or a clinician
    if not (check_is_worker(user_data) or check_is_clinician(user_data)):
        return response  # Return response if the user isn't authorized

    # Get current username from the JWT
    current_user = get_user_from_token()['username']

    if request.method == 'POST':
        new_username = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")  # This might be empty
        email = request.form.get("email")

        # Ensure the new username is unique
        if new_username != current_user and check_user_exists(new_username):
            return redirect(url_for('profile.view_worker', error="Username already exists."))

        # Hash password if provided, otherwise don't update it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None

        # Call update_user, but **only pass password if it's provided**
        if password:
            update_user(username=current_user, 
                        new_username=new_username, 
                        name=name, 
                        password=hashed_password, 
                        email=email)
        else:
            update_user(username=current_user, 
                        new_username=new_username, 
                        name=name, 
                        email=email)  # No password update

        return redirect(url_for('profile.view_worker'))  # Redirect to profile view after update



