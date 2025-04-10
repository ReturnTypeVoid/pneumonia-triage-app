import bcrypt
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from routes.auth import check_jwt_tokens, check_is_admin, get_user_from_token
from db import get_user, get_settings, update_twilio_settings, update_smtp_settings

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=['GET'])
def edit_settings():
    """
    Route to view and edit system settings.

    Description:
        Loads the current application settings and shows them on the settings page.
        Only accessible to admins.

    Arguments:
        None

    Returns:
        Response: Renders the settings page.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response
    
    current_user = get_user_from_token()['username']
    settings = get_settings()

    return render_template('settings/settings.html', current_user=get_user(current_user), settings=settings)

@settings.route('/settings/twilio', methods=['POST'])
def update_twilio():
    """
    Route to update Twilio integration settings.

    Description:
        Lets an admin update Twilio credentials and phone number for SMS features.
        Saves the new values and flashes a message based on the result.

    Arguments:
        None

    Returns:
        Response: Redirects back to the settings page.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    success = update_twilio_settings(
        request.form.get('twilio_account_id'), 
        request.form.get('twilio_secret_key'), 
        request.form.get('twilio_phone')
    )
    
    session.pop('_flashes', None)

    if success:
        flash("Twilio settings updated successfully.", "success")
    else:
        flash("Failed to update Twilio settings.", "error")

    return redirect(url_for('settings.edit_settings'))

@settings.route('/settings/smtp', methods=['POST'])
def update_smtp():
    """
    Route to update SMTP email settings.

    Description:
        Allows an admin to update email server settings like server address, port,
        TLS usage, login credentials, and sender address.

    Arguments:
        None

    Returns:
        Response: Redirects back to the settings page after saving.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response
     
    smtp_tls = 'smtp_tls' in request.form

    success = update_smtp_settings(
        request.form.get('smtp_server'),
        int(request.form.get('smtp_port')),
        smtp_tls,
        request.form.get('smtp_username'),
        request.form.get('smtp_password'),
        request.form.get('smtp_sender')
    )

    session.pop('_flashes', None)

    if success:
        flash("SMTP settings updated successfully.", "success")
    else:
        flash("Failed to update SMTP settings.", "error")

    return redirect(url_for('settings.edit_settings'))
