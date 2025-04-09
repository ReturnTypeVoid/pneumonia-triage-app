import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from routes.auth import check_jwt_tokens, check_is_worker, get_user_from_token, check_is_clinician
from db import add_patient, get_user, get_user_id, list_patients, patients_to_review, all_pneumonia_cases, reviewed_patients, delete_patient, update_patient, get_patient, delete_xray_image, get_closed_cases, close_patient_case, reopen_patient_case, get_reviewed_cases_for_worker, update_clinician_reviewed, update_clinician_to_review
from datetime import datetime
patients = Blueprint('patients', __name__)

@patients.route('/patients/new', methods=['GET', 'POST'])
def new_patient():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    if not check_is_worker(user_data):
        return response

    current_user = get_user_from_token()['username']

    def convert_bool(value):
        return 1 if value == "True" else 0

    if request.method == 'POST':

        # Contact Information
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        address = request.form.get('address')
        address_2 = request.form.get('address_2')
        city = request.form.get('city')
        state = request.form.get('state')
        zip = request.form.get('zip')  
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Healthcare
        dob = request.form.get('dob')
        sex = request.form.get('sex')

        try:
            height = float(request.form.get('height', 0))
            weight = float(request.form.get('weight', 0))
        except ValueError:
            height = 0.0
            weight = 0.0

        blood_type = request.form.get('blood_type')  
        smoker_status = request.form.get('smoker_status')
        alcohol_consumption = request.form.get('alcohol_consumption')  
        allergies = request.form.get('allergies')
        vaccination_history = request.form.get('vaccination_history')

        # Symptoms
        fever = convert_bool(request.form.get('fever'))
        cough = convert_bool(request.form.get('cough'))

        try:
            cough_duration = int(request.form.get('cough_duration', 0))
        except ValueError:
            cough_duration = 0

        cough_type = request.form.get('cough_type')
        chest_pain = convert_bool(request.form.get('chest_pain'))
        shortness_of_breath = convert_bool(request.form.get('shortness_of_breath'))  
        fatigue = convert_bool(request.form.get('fatigue'))
        chills_sweating = convert_bool(request.form.get('chills_sweating'))

        # Worker notes
        worker_notes = request.form.get('worker_notes')

        worker_id = get_user_id(current_user)
        last_updated = datetime.now().strftime('%Y-%m-%d')

        add_patient(
            first_name, surname, address, city, state, zip, dob, sex, height, weight, blood_type,
            smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, 
            chest_pain, shortness_of_breath, fatigue, chills_sweating, last_updated, worker_id,  
            address_2, email, phone, cough_duration, cough_type, worker_notes
        )

        return redirect(url_for('patients.get_worker_patients'))

    return render_template('/patients/patient_form.html', user=get_user(current_user), current_user=get_user(current_user), patient=None)

@patients.route('/patients/')
def get_worker_patients():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response
    
    current_user = get_user_from_token()['username']

    
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))  
    per_page = 15  
    
    
    patients = list_patients(search_query)  

    
    total_patients = len(patients)
    total_pages = (total_patients + per_page - 1) // per_page  
    start = (page - 1) * per_page
    end = start + per_page
    paginated_patients = patients[start:end]   

    return render_template('patients/patient_list.html',  
        current_page=page, total_pages=total_pages, search_query=search_query, patients=paginated_patients, user = get_user(current_user), current_user=get_user(current_user), tab="worker_all")

@patients.route('/patients/reviewing')
def patients_reviewing():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_clinician, response = check_is_clinician(user_data)
    if not is_clinician:
        return response

    current_user = get_user_from_token().get('username')
    if not current_user:
        return "Invalid User", 403

    user = get_user(current_user)
    if not user:
        return "User not found", 404

    # Search + pagination
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 15

    patients = patients_to_review(search_query)
    print(f"Search query: {search_query}")
    print(f"Total patients found: {len(patients)}")

    total_patients = len(patients)
    total_pages = (total_patients + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_patients = patients[start:end]

    return render_template(
        'patients/patient_list.html',
        patients=paginated_patients,
        current_user=user,
        user=user,  # if the template expects both
        current_page=page,
        total_pages=total_pages,
        search_query=search_query,
        filter_type="",
        tab = "reviewing"
    )

@patients.route('/patients/reviewed')
def patients_reviewed():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_clinician, response = check_is_clinician(user_data)
    if not is_clinician:
        return response

    user_info = get_user_from_token()
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403

    current_user = user_info['username']
    user = get_user(current_user)
    if not user:
        return "User not found", 404

    search_query = request.args.get('search', '').strip()
    patients = reviewed_patients(search_query)

    return render_template(
        'patients/patient_list.html',
        patients=patients,
        current_user=user,
        user=user,
        search_query=search_query,
        filter_type="",
        tab = "reviewed"
    )

@patients.route('/patients/pneumonia-cases')
def pneumonia_cases():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_clinician, response = check_is_clinician(user_data)
    if not is_clinician:
        return response

    user_info = get_user_from_token()
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403

    current_user = user_info['username']
    user = get_user(current_user)
    if not user:
        return "User not found", 404

    search_query = request.args.get('search', '').strip()
    patients = all_pneumonia_cases(search_query)

    return render_template(
        'patients/patient_list.html',
        patients=patients,
        current_user=user,
        user=user,
        search_query=search_query,
        filter_type="",
        tab = "pneumonia"
    )

@patients.route('/patients/closed')
def closed_cases():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    role = user_data.get("role")
    if role not in ["clinician", "worker"]:
        return "Unauthorized", 403

    user_info = get_user_from_token()
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403

    current_user = user_info['username']
    user = get_user(current_user)
    if not user:
        return "User not found", 404

    search_query = request.args.get('search', '').strip()
    patients = get_closed_cases(search_query)

    return render_template(
        'patients/patient_list.html',
        patients=patients,
        current_user=user,
        user=user,
        search_query=search_query,
        filter_type="",
        tab = "closed"
    )

@patients.route('/patients/close/<int:id>', methods=['POST'])
def close_case(id):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    role = user_data.get("role")
    if role not in ["clinician", "worker"]:
        return "Unauthorized", 403

    session.pop('_flashes', None)

    success = close_patient_case(id)

    if success:
        flash("Case closed successfully.", "success")
    else:
        flash("Failed to close case.", "error")

    return redirect(url_for('patients.closed_cases'))

@patients.route('/patients/open/<int:id>', methods=['POST'])
def reopen_case(id):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    role = user_data.get("role")
    if role not in ["clinician", "worker"]:
        return "Unauthorized", 403

    session.pop('_flashes', None)  # Clear existing messages

    success = reopen_patient_case(id)

    if success:
        flash("Case reopened successfully.", "success")
    else:
        flash("Failed to reopen case.", "error")

    return redirect(url_for('patients.get_worker_patients'))

@patients.route('/patients/delete/<int:id>', methods=['POST'])
def delete_existing_patient(id):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_worker, response = check_is_worker(user_data)
    if not is_worker:
        return response

    success = delete_patient(id)

    if success:
        flash("Case deleted successfully.", "success")
    else:
        flash("Failed to delete case.", "error")

    return redirect(url_for('patients.get_worker_patients')) 

@patients.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    current_user = get_user_from_token().get('username')
    if not current_user:
        return "Invalid User", 403


    def convert_bool(value):
        return 1 if value == "True" else 0

    if request.method == 'POST':
        # Contact Information
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        address = request.form.get('address')
        address_2 = request.form.get('address_2')
        city = request.form.get('city')
        state = request.form.get('state')
        zip = request.form.get('zip')  
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Healthcare
        dob = request.form.get('dob')
        sex = request.form.get('sex')

        try:
            height = float(request.form.get('height', 0))
            weight = float(request.form.get('weight', 0))
        except ValueError:
            height = 0.0
            weight = 0.0

        blood_type = request.form.get('blood_type')  
        smoker_status = request.form.get('smoker_status')
        alcohol_consumption = request.form.get('alcohol_consumption')  
        allergies = request.form.get('allergies')
        vaccination_history = request.form.get('vaccination_history')

        # Symptoms
        fever = convert_bool(request.form.get('fever'))
        cough = convert_bool(request.form.get('cough'))

        try:
            cough_duration = int(request.form.get('cough_duration', 0))
        except ValueError:
            cough_duration = 0

        cough_type = request.form.get('cough_type')
        chest_pain = convert_bool(request.form.get('chest_pain'))
        shortness_of_breath = convert_bool(request.form.get('shortness_of_breath'))  
        fatigue = convert_bool(request.form.get('fatigue'))
        chills_sweating = convert_bool(request.form.get('chills_sweating'))

        # Worker Notes
        worker_notes = request.form.get('worker_notes')
        pneumonia_confirmed = convert_bool(request.form.get('pneumonia_confirmed'))
        clinician_note = request.form.get('clinician_notes')
        last_updated = datetime.now().strftime('%Y-%m-%d')

        if clinician_note != '':
            update_clinician_reviewed(id, 1)
            update_clinician_to_review(id, 0)

        update_patient(
            patient_id=id,
            first_name=first_name,
            surname=surname,
            address=address,
            address_2=address_2,
            city=city,
            state=state,
            zip=zip,
            email=email,
            phone=phone,
            dob=dob,
            sex=sex,
            height=height,
            weight=weight,
            blood_type=blood_type,
            smoker_status=smoker_status,
            alcohol_consumption=alcohol_consumption,
            allergies=allergies,
            vaccination_history=vaccination_history,
            fever=fever,
            cough=cough,
            cough_duration=cough_duration,
            cough_type=cough_type,
            chest_pain=chest_pain,
            shortness_of_breath=shortness_of_breath,
            fatigue=fatigue,
            chills_sweating=chills_sweating,
            worker_notes=worker_notes,
            last_updated=last_updated,
            pneumonia_confirmed=pneumonia_confirmed,
            clinician_note=clinician_note
        )
        is_worker, response = check_is_worker(user_data)
        is_clinician, response = check_is_clinician(user_data)

        if is_worker:
            return redirect(url_for('patients.get_worker_patients'))
        elif is_clinician:
            return redirect(url_for('patients.patients_reviewed'))
        return redirect(url_for('auth.login'))
    
    return render_template('patients/patient_form.html', user=get_user(current_user), current_user=get_user(current_user), patient=get_patient(id))

@patients.route('/patients/triage')
def workers_follow_ups():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response

    current_user = get_user_from_token().get('username')
    user = get_user(current_user)

    if not user:
        return "User not found", 404

    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 15

    all_patients = get_reviewed_cases_for_worker()

    return render_template(
        'patients/patient_list.html',
        current_user=user,
        user=user,
        patients=all_patients,
        current_page=page,
        search_query=search_query,
        filter_type="",
        tab="followups"
    )