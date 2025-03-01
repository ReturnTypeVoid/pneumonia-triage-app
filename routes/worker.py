from flask import Blueprint, request, render_template, redirect, url_for, make_response, session
import requests
from routes.auth import get_user_from_token, clear_session 
from db import get_db_connection

worker = Blueprint('worker', __name__)

def list_patients():
    # Get a connection to the database
    conn = get_db_connection()
    c = conn.cursor()

    # Fetch patient data from the database
    c.execute('''
        SELECT id, first_name, surname, address, address_2, city, state, zip, email, phone, dob, sex,
               height, weight, blood_type, smoker_status, allergies, vaccination_history,
               fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, worker_id, clinician_id
        FROM patients
    ''')
    patients = c.fetchall()
    conn.close()

    return patients

@worker.route('/dashboard')
def dashboard():
    response = make_response()
    user_data = get_user_from_token()

    if not user_data or user_data['role'] != 'worker':
        response = make_response(redirect(url_for('auth.login')))
        clear_session(response)
        return response

    # refresh token if it's expired
    refresh_token = request.cookies.get('refresh_token')
    if not user_data and refresh_token:
        refresh_response = requests.post(url_for('auth.refresh', _external=True), cookies=request.cookies)
        if refresh_response.status_code == 200:
            new_access_token = refresh_response.cookies.get('access_token')
            response.set_cookie('access_token', new_access_token, httponly=True, secure=True)
            user_data = get_user_from_token()
        else:
            response = make_response(redirect(url_for('auth.login')))
            clear_session(response)
            return response
    
    return render_template('worker/dashboard.html', patients=list_patients())
