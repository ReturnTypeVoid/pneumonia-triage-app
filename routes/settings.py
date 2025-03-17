import bcrypt
from flask import Blueprint, request, render_template, redirect, url_for, flash
from routes.auth import check_jwt_tokens, check_is_admin, get_user_from_token
from db import get_user, get_settings, update_twilio_settings, update_smtp_settings

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=['GET'])
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


@settings.route('/settings/twilio', methods=['POST'])
def update_twilio():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    update_twilio_settings(
        request.form.get('twilio_account_id'), 
        request.form.get('twilio_secret_key'), 
        request.form.get('twilio_phone')
    )

    flash("Twilio settings updated successfully!", "twilio_success")
    return redirect(url_for('settings.edit_settings'))


@settings.route('/settings/smtp', methods=['POST'])
def update_smtp():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    update_smtp_settings(
        request.form.get('smtp_server'),
        request.form.get('smtp_port'),
        request.form.get('smtp_tls') == 'on',  # Convert checkbox to bool
        request.form.get('smtp_username'),
        request.form.get('smtp_password'),
        request.form.get('smtp_sender')
    )

    flash("SMTP settings updated successfully!", "smtp_success")
    return redirect(url_for('settings.edit_settings'))
