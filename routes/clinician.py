# from flask import Blueprint, request, render_template, redirect, url_for
# from routes.auth import check_jwt_tokens, check_is_clinician, get_user_from_token 
# from db import list_patients, get_user  

# clinician = Blueprint('clinician', __name__)

# @clinician.route('/dashboard')
# def dashboard():
#     user_data, response = check_jwt_tokens()
#     if not user_data:
#         return response

#     user_data, response = check_is_clinician(user_data)
#     if not user_data:
#         return response
    
#     current_user = get_user_from_token()['username']

#     return render_template('clinician/dashboard.html', current_user=get_user(current_user), patients=list_patients()) 

from flask import Blueprint, request, render_template, url_for
from routes.auth import check_jwt_tokens, check_is_clinician, get_user_from_token
from db import patient_list_ai_detect, get_user  


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
    patients = patient_list_ai_detect()
    
    # Render the dashboard template
    return render_template('clinician/patient_cond.html', user=user, patients=patients, current_user=current_user)


    

    # Search query (optional)
    # search_query = request.args.get('search_query', '').strip()

    # #  Get AI-flagged patients (diagnosed with pneumonia or whatever AI finds)
    # patients = list_patients_flagged_by_ai()

    # #  Filter by search query (name, ID, etc.)
    # if search_query:
    #     patients = [
    #         patient for patient in patients
    #         if search_query.lower() in str(patient.get('id', '')).lower()
    #         or search_query.lower() in (patient.get('first_name', '') + ' ' + patient.get('surname', '')).lower()
    #         or search_query.lower() in patient.get('condition', '').lower()
    #         or search_query.lower() in patient.get('status', '').lower()
    #     ]

    # return render_template(
    #     'clinician/dashboard.html',
    #     patients=patients,
    #     search_query=search_query,
    #     user=user,
    #     current_user=user
    # )
