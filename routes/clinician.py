from flask import Blueprint, request, render_template, url_for, redirect
from routes.auth import check_jwt_tokens, check_is_clinician, get_user_from_token
from db import patient_list_ai_detect, list_patients, get_user, reviewed_patients, patients_to_review, all_pneumonia_cases 


clinician = Blueprint('clinician', __name__)

@clinician.route('/clinician/dashboard')
def dashboard():
    """
    Displays all patients flagged by AI for clinician review.
    """

    # Authenticate JWT
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    # Verify clinician role
    is_clinician, response = check_is_clinician(user_data)
    if not is_clinician:
        return response
    
    token = request.cookies.get('access_token')  # token is stored in cookies
    if not token:
        return "Unauthorized", 401  # No token found
    
    user_info = get_user_from_token()  # Pass the token correctly
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403  # Handle missing username
    
    current_user = user_info['username']
    
    #Fetch user data from the database
    user = get_user(current_user)
    if not user:
        return "User not found", 404  # Handle user not found in DB
    
    #Fetch patient data from the database
    patients = list_patients()
    # patients = patient_list_ai_detect()
    
    # Render the dashboard template
    #return render_template('clinician/patient_cond.html', user = get_user(current_user), patients=patients, current_user=get_user(current_user))
    return redirect(url_for('clinician.patients_reviewing'))

@clinician.route('/patients/reviewing')
def patients_reviewing():
    # Authenticate JWT
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    # Verify clinician role
    is_clinician, response = check_is_clinician(user_data)
    if not is_clinician:
        return response
    
    token = request.cookies.get('access_token')
    if not token:
        return "Unauthorized", 401
    
    user_info = get_user_from_token()
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403
    
    current_user = user_info['username']
    
    user = get_user(current_user)
    if not user:
        return "User not found", 404
    
    # Get patients flagged by AI for review
    patients = patients_to_review()
    
    return render_template('clinician/patient_cond.html', patients=patients, current_user=user)


@clinician.route('/patients/reviewed')
def patients_reviewed():
    # Authenticate JWT
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    # Verify clinician role
    is_clinician, response = check_is_clinician(user_data)
    if not is_clinician:
        return response
    
    token = request.cookies.get('access_token')
    if not token:
        return "Unauthorized", 401
    
    user_info = get_user_from_token()
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403
    
    current_user = user_info['username']
    
    user = get_user(current_user)
    if not user:
        return "User not found", 404
    
    # Get the reviewed patients with clinician notes
    patients = reviewed_patients()
    
    return render_template('clinician/patient_cond.html', patients=patients, current_user=user)


@clinician.route('/pneumonia-cases')
def pneumonia_cases():
    # Authenticate JWT
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    # Verify clinician role
    is_clinician, response = check_is_clinician(user_data)
    if not is_clinician:
        return response
    
    token = request.cookies.get('access_token')
    if not token:
        return "Unauthorized", 401
    
    user_info = get_user_from_token()
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403
    
    current_user = user_info['username']
    
    user = get_user(current_user)
    if not user:
        return "User not found", 404
    
    # Get patients whether they have clinician notes or not
    patients = all_pneumonia_cases()
    
    return render_template('clinician/patient_cond.html', patients=patients, current_user=user)
