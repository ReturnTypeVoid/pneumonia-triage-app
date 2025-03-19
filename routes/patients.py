import os
from flask import Blueprint, request, render_template, redirect, url_for
from routes.auth import check_jwt_tokens, check_is_worker, get_user_from_token, check_is_clinician
from db import add_patient, get_user, get_user_id, list_patients, patients_to_review, all_pneumonia_cases, reviewed_patients, delete_patient, update_patient, get_patient, delete_xray_image
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

    if request.method == 'POST':
        
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
        
        
        try:
            height = float(request.form.get('height', 0))
            weight = float(request.form.get('weight', 0))
        except ValueError:
            height = 0.0
            weight = 0.0

        blood = request.form.get('blood')
        smoker_status = request.form.get('smoker_status')
        alcohol = request.form.get('alcohol')
        allergies = request.form.get('allergies')
        vaccination_history = request.form.get('vaccination_history')

        
        def convert_bool(value):
            return True if value == "Yes" else False

        fever = convert_bool(request.form.get('fever'))
        cough = convert_bool(request.form.get('cough'))

        
        try:
            cough_duration = int(request.form.get('cough_duration', 0))
        except ValueError:
            cough_duration = 0

        cough_type = request.form.get('cough_type')
        chest_pain = convert_bool(request.form.get('chest_pain'))
        shortness_of_breath = convert_bool(request.form.get('breath'))
        fatigue = convert_bool(request.form.get('fatigue'))
        chills_sweating = convert_bool(request.form.get('chills'))

        worker_id = get_user_id(current_user)  
        last_updated = datetime.now().strftime('%Y-%m-%d')  

        
        add_patient(
            first_name, surname, address, city, state, zip_code, dob, sex, height, weight, blood,
            smoker_status, alcohol, allergies, vaccination_history, fever, cough, cough_duration, 
            cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id,
            address2, email, phone, last_updated=last_updated
        )

        return redirect(url_for('patients.get_worker_patients'))  

    return render_template('/patients/patient_form.html', user=get_user(current_user), current_user=get_user(current_user))

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
        current_page=page, total_pages=total_pages, search_query=search_query, patients=paginated_patients, user = get_user(current_user), current_user=get_user(current_user))

@patients.route('/patients/reviewing')
def patients_reviewing():
    
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    
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
    
    
    patients = patients_to_review()
    
    return render_template('patients/patient_list.html', patients=patients, current_user=user)

@patients.route('/patients/reviewed')
def patients_reviewed():
    
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response
    
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
    
    patients = reviewed_patients()
    
    return render_template('patients/patient_list.html', patients=patients, current_user=user)

@patients.route('/pneumonia-cases')
def pneumonia_cases():
    
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    
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
    
    
    patients = all_pneumonia_cases()
    
    return render_template('patients/patient_list.html', patients=patients, current_user=user)

@patients.route('/patients/delete/<id>', methods=['POST'])
def delete_existing_patient(id):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response 

    is_worker, response = check_is_worker(user_data)
    if not is_worker:
        return response

    delete_patient(id)

    return redirect(url_for('patients.get_worker_patients')) 

@patients.route('/patients/edit/<id>', methods=['GET', 'POST'])
def edit_patient(id):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    if not check_is_worker(user_data):
        return response

    current_user = get_user_from_token()['username']

    def convert_bool(value):
        return 1 if value == "True" else 0

    if request.method == 'POST':
        
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        address = request.form.get('address')
        address_2 = request.form.get('address_2')
        city = request.form.get('city')
        state = request.form.get('state')
        zip = request.form.get('zip')  
        email = request.form.get('email')
        phone = request.form.get('phone')
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
        alcohol_consumption = request.form.get('alcohol')  
        allergies = request.form.get('allergies')
        vaccination_history = request.form.get('vaccination_history')

        


        fever = convert_bool(request.form.get('fever'))
        cough = convert_bool(request.form.get('cough'))
        chest_pain = convert_bool(request.form.get('chest_pain'))
        shortness_of_breath = convert_bool(request.form.get('shortness_of_breath'))  
        fatigue = convert_bool(request.form.get('fatigue'))
        chills_sweating = convert_bool(request.form.get('chills_sweating'))  

        try:
            cough_duration = int(request.form.get('cough_duration', 0))
        except ValueError:
            cough_duration = 0

        cough_type = request.form.get('cough_type')

        last_updated = datetime.now().strftime('%Y-%m-%d')

        
        update_patient(
            patient_id=id,
            first_name=first_name,
            surname=surname,
            address=address,
            address_2=address_2,  
            city=city,
            state=state,
            zip=zip,  
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
            email=email,
            phone=phone,
            last_updated=last_updated
        )

        return redirect(url_for('patients.get_worker_patients'))

    return render_template('patients/patient_form.html', user=get_user(current_user), current_user=get_user(current_user), patient=get_patient(id))

@patients.route('/patients/xray/delete/<id>', methods=['POST'])
def delete_xray(id):
    
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response  

    
    if not (check_is_worker(user_data) or check_is_clinician(user_data)):
        return response  

    
    patient = get_patient(id)
    if not patient or not patient['xray_img']:  
        return redirect(url_for('patients.edit_patient', id=id))

    
    delete_xray_image(id)  

    return redirect(url_for('patients.edit_patient', id=id))

