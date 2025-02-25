from flask import render_template
from db import get_db_connection

def list_patients():
    # Get a connection to the database
    conn = get_db_connection()
    c = conn.cursor()

    # Fetch patient data from the database
    c.execute('''
        SELECT id, first_name, surname, address, address_2, city, state, zip, email, phone, dob, sex,
               height, weight, blood_type, smoker_status, allergies, vaccination_history,
               fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, worker_id, clinician_id
        FROM patient
    ''')
    patients = c.fetchall()
    conn.close()

    # Render the worker dashboard template with the patient data
    return render_template('worker/dashboard.html', patients=patients)


# this file is basically a copy of admin.pym but with different set of fields retrieved from SQL db, and passing them to different dashboard with different data - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT