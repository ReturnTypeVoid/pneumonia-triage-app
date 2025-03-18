from flask import Blueprint, request, render_template, redirect, url_for
from routes.auth import check_jwt_tokens, check_is_worker, get_user_from_token, check_is_clinician
from db import add_patient, get_user, get_user_id, list_patients, patient_list_ai_detect, patients_to_review, all_pneumonia_cases, reviewed_patients

patients = Blueprint('patients', __name__)

@patients.route('/patients/new', methods=['GET', 'POST'])
def new_patient():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    if not check_is_worker(user_data):
        return response
    
    current_user = get_user_from_token()['username']

    if request.method == 'POST':
        # Extract form data
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        address = request.form.get('address')
        address2 = request.form.get('address2')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        sex = request.form.get('sex')
        height = request.form.get('height')
        weight = request.form.get('weight')
        blood = request.form.get('blood')
        smoker_status = request.form.get('smoker_status')
        alcohol = request.form.get('alcohol')
        allergies = request.form.get('allergies')
        vaccination_history = request.form.get('vaccination_history')
        fever = request.form.get('fever')
        cough = request.form.get('cough')
        cough_duration = request.form.get('cough_duration')
        cough_type = request.form.get('cough_type')
        chest_pain = request.form.get('chest_pain')
        breath = request.form.get('breath')
        fatigue = request.form.get('fatigue')
        chills = request.form.get('chills')

        worker_id = get_user_id(current_user) # Assign current user as worker_id
        clinician_id = None  # Leave as NULL until assigned
        xray_img = None  # Placeholder

        # Convert boolean-like values from form
        def convert_bool(value):
            return True if value == "Yes" else False

        fever = convert_bool(fever)
        cough = convert_bool(cough)
        chest_pain = convert_bool(chest_pain)
        breath = convert_bool(breath)
        fatigue = convert_bool(fatigue)
        chills = convert_bool(chills)

        # Call add_patient function
        add_patient(
            first_name, surname, address, city, state, zip_code, dob, sex, height, weight, blood,
            smoker_status, alcohol, allergies, vaccination_history, fever, cough, cough_duration, 
            cough_type, chest_pain, breath, fatigue, chills, worker_id, address2, email, phone
        )

        return redirect(url_for('patients.get_worker_patients'))  # Redirect back to the form

    return render_template('/patient/patient_form.html', user = get_user(current_user), current_user=get_user(current_user))

@patients.route('/patients/')
def get_worker_patients():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response
    
    current_user = get_user_from_token()['username']

    # Get search query from request
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))  # Current page (pagination)
    per_page = 15  # Number of patients per page
    
    #Call list_patients with search_query
    patients = list_patients(search_query)  

    # Pagination logic
    total_patients = len(patients)
    total_pages = (total_patients + per_page - 1) // per_page  # Ceiling division
    start = (page - 1) * per_page
    end = start + per_page
    paginated_patients = patients[start:end]   

    return render_template('worker/list_patients.html',  
        current_page=page, total_pages=total_pages, search_query=search_query, patients=paginated_patients, user = get_user(current_user), current_user=get_user(current_user))

@patients.route('/patients/')
def get_clinician_patients():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_clinician(user_data)
    if not user_data:
        return response
    
    current_user = get_user_from_token()['username']

    # Get search query from request
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))  # Current page (pagination)
    per_page = 15  # Number of patients per page
    
    #Call Patient lists detected by ai with search_query
    patients = patient_list_ai_detect()  

    # Pagination logic
    total_patients = len(patients)
    total_pages = (total_patients + per_page - 1) // per_page  # Ceiling division
    start = (page - 1) * per_page
    end = start + per_page
    paginated_patients = patients[start:end]   

    return render_template('clinician/patient_cond.html',  
        current_page=page, total_pages=total_pages, search_query=search_query, patients=paginated_patients, user = get_user(current_user), current_user=get_user(current_user))

@patients.route('/patients/reviewing')
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


@patients.route('/patients/reviewed')
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


@patients.route('/pneumonia-cases')
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
