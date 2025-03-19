import sqlite3

def get_connection():
    """Returns a database connection to SQLite"""
    connection = sqlite3.connect('database/database.db')
    connection.row_factory = sqlite3.Row  # this should allow accessing columns by name - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT
    return connection

def get_users():
    # Connect to the database
    connection = get_connection()
    cursor = connection.cursor()

    # sql query, storing the returned data in users var - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT
    cursor.execute('SELECT id, name, username, role FROM users')

    users = cursor.fetchall()  
    connection.close()  # Close the database connection - Should ALWAYS close when finished - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT

    return users

def get_user(username):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

    user = cursor.fetchone()
    connection.close()
    
    return user

def get_user_id(username):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    
    connection.close()
    
    return user_id[0] if user_id else None  # Return the ID or None if not found

def check_user_exists(username):
    return get_user(username) is not None

def add_user(name, username, password, role, email):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO users (name, username, password, role, email)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username) DO NOTHING
    ''', (name, username.lower(), password, role, email))  # Convert to lowercase

    connection.commit()
    connection.close()

def update_user(username, new_username=None, name=None, password=None, role=None, email=None):
    connection = get_connection()
    cursor = connection.cursor()

    updates = {}
    if new_username:
        updates["username"] = new_username.lower()  # Convert new username to lowercase
    if name:
        updates["name"] = name
    if password:
        updates["password"] = password
    if role:
        updates["role"] = role
    if email:
        updates["email"] = email

    if not updates:
        return

    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [username.lower()]  # Convert current username to lowercase

    query = f"UPDATE users SET {set_clause} WHERE username = ?"

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

def delete_user(username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE from users WHERE username =?", (username,))

    connection.commit()
    connection.close()

def get_settings():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM settings WHERE id = 1;')
    settings = cursor.fetchone()
    
    connection.close()

    return settings

def update_twilio_settings(twilio_account_id=None, twilio_secret_key=None, twilio_phone=None):
    connection = get_connection()
    cursor = connection.cursor()

    updates = {}
    if twilio_account_id:
        updates["twilio_account_id"] = twilio_account_id
    if twilio_secret_key:
        updates["twilio_secret_key"] = twilio_secret_key
    if twilio_phone:
        updates["twilio_phone"] = twilio_phone

    if not updates:
        return  # No updates to make

    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [1]  # ID is always 1

    query = f"UPDATE settings SET {set_clause} WHERE id = ?"
    
    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

def update_smtp_settings(smtp_server=None, smtp_port=None, smtp_tls=None, smtp_username=None, smtp_password=None, smtp_sender=None):
    connection = get_connection()
    cursor = connection.cursor()

    updates = {}
    if smtp_server:
        updates["smtp_server"] = smtp_server
    if smtp_port:
        updates["smtp_port"] = smtp_port
    if smtp_tls is not None:  # Boolean values should be explicitly checked
        updates["smtp_tls"] = smtp_tls
    if smtp_username:
        updates["smtp_username"] = smtp_username
    if smtp_password:
        updates["smtp_password"] = smtp_password
    if smtp_sender:
        updates["smtp_sender"] = smtp_sender

    if not updates:
        return  # No updates to make

    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [1]  # ID is always 1

    query = f"UPDATE settings SET {set_clause} WHERE id = ?"

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

def update_user_image(username, profile_img):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE users SET profile_img = ? WHERE username = ?", (profile_img, username))

    connection.commit()
    cursor.close()
    connection.close()

def get_user_image(username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT profile_img FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0] if result else None

def list_patients(search_query=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, email, phone, dob, allergies, vaccination_history,
               clinician_id, last_updated, clinician_note
        FROM patients
    '''
    
    params = []
    
    if search_query:
        query += '''
        WHERE LOWER(first_name) LIKE ? 
           OR LOWER(surname) LIKE ?
           OR LOWER(email) LIKE ?
           OR LOWER(phone) LIKE ?
        '''
        search_pattern = f"%{search_query.lower()}%"
        params = [search_pattern] * 4

    # Ensure sorting by last_updated (oldest first)
    query += " ORDER BY last_updated ASC"

    cursor.execute(query, params)
    patients = cursor.fetchall()
    connection.close()

    return patients

def patient_list_ai_detect():
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, verified_ai
        FROM patients
        WHERE ai_suspected = TRUE
        AND verified_ai IS NULL
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()

    # Now convert ai_suspected and verified_ai to human-readable format
    patient_list = []
    for row in rows:
        patient_dict = dict(row)
        
        # Map ai_suspected boolean to "Pneumonia"
        if patient_dict['ai_suspected']:
            patient_dict['status'] = 'Pneumonia'
        else:
            patient_dict['status'] = 'No issues detected'

        # Map verified_ai boolean to something human-friendly
        if patient_dict['verified_ai'] is None:
            patient_dict['condition'] = 'Pending Review'
        elif patient_dict['verified_ai']:
            patient_dict['condition'] = 'Confirmed Pneumonia'
        else:
            patient_dict['condition'] = 'Not Pneumonia'

        # Remove raw booleans if not needed
        # del patient_dict['ai_suspected']
        # del patient_dict['verified_ai']
        
        patient_list.append(patient_dict)

    return patient_list

def add_patient(
    first_name, surname, address, city, state, zip_code, dob, sex, height, weight, blood,
    smoker_status, alcohol, allergies, vaccination_history, fever, cough, cough_duration, 
    cough_type, chest_pain, breath, fatigue, chills, worker_id, address2=None, email=None, phone=None,
    last_updated=None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO patients (
            first_name, surname, address, address_2, city, state, zip, email, phone, 
            dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, 
            allergies, vaccination_history, fever, cough, cough_duration, cough_type, 
            chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, 
            last_updated  -- This was missing before
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        first_name, surname, address, address2, city, state, zip_code, email, phone,
        dob, sex, height, weight, blood, smoker_status, alcohol, 
        allergies, vaccination_history, fever, cough, cough_duration, 
        cough_type, chest_pain, breath, fatigue, chills, worker_id, last_updated
    ))

    connection.commit()
    connection.close()

def patients_to_review():
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, verified_ai, clinician_note
        FROM patients
        WHERE ai_suspected = TRUE
        AND (clinician_note IS NULL OR clinician_note = '')
        AND verified_ai IS NULL
    '''

    cursor.execute(query)
    patients = cursor.fetchall()
    connection.close()

    return patients  # No need to convert to dictionaries manually

def reviewed_patients():
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, verified_ai, clinician_note
        FROM patients
        WHERE ai_suspected = TRUE
        AND clinician_note IS NOT NULL
        AND clinician_note != ''
        AND verified_ai IS NOT NULL
    '''

    cursor.execute(query)
    patients = cursor.fetchall()
    connection.close()

    return patients

def all_pneumonia_cases():
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, verified_ai, clinician_note
        FROM patients
        WHERE ai_suspected = TRUE
    '''

    cursor.execute(query)
    patients = cursor.fetchall()  # Returns sqlite3.Row objects
    connection.close()

    return patients  # No processing, just return raw data

def delete_patient(patient_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))

    connection.commit()
    connection.close()

def update_patient(patient_id, first_name=None, surname=None, address=None, address_2=None, city=None, 
                   state=None, zip=None, email=None, phone=None, dob=None, sex=None, height=None, 
                   weight=None, blood_type=None, smoker_status=None, alcohol_consumption=None, 
                   allergies=None, vaccination_history=None, fever=None, cough=None, cough_duration=None, 
                   cough_type=None, chest_pain=None, shortness_of_breath=None, fatigue=None, 
                   chills_sweating=None, worker_id=None, clinician_id=None, xray_img=None, 
                   ai_suspected=None, verified_ai=None, clinician_note=None, last_updated=None):

    connection = get_connection()
    cursor = connection.cursor()

    updates = {}
    if first_name is not None:
        updates["first_name"] = first_name
    if surname is not None:
        updates["surname"] = surname
    if address is not None:
        updates["address"] = address
    if address_2 is not None:
        updates["address_2"] = address_2
    if city is not None:
        updates["city"] = city
    if state is not None:
        updates["state"] = state
    if zip is not None:
        updates["zip"] = zip
    if email is not None:
        updates["email"] = email
    if phone is not None:
        updates["phone"] = phone
    if dob is not None:
        updates["dob"] = dob
    if sex is not None:
        updates["sex"] = sex
    if height is not None:
        updates["height"] = height
    if weight is not None:
        updates["weight"] = weight
    if blood_type is not None:
        updates["blood_type"] = blood_type
    if smoker_status is not None:
        updates["smoker_status"] = smoker_status
    if alcohol_consumption is not None:
        updates["alcohol_consumption"] = alcohol_consumption
    if allergies is not None:
        updates["allergies"] = allergies
    if vaccination_history is not None:
        updates["vaccination_history"] = vaccination_history
    if fever is not None:
        updates["fever"] = fever
    if cough is not None:
        updates["cough"] = cough
    if cough_duration is not None:
        updates["cough_duration"] = cough_duration
    if cough_type is not None:
        updates["cough_type"] = cough_type
    if chest_pain is not None:
        updates["chest_pain"] = chest_pain
    if shortness_of_breath is not None:
        updates["shortness_of_breath"] = shortness_of_breath
    if fatigue is not None:
        updates["fatigue"] = fatigue
    if chills_sweating is not None:
        updates["chills_sweating"] = chills_sweating
    if worker_id is not None:
        updates["worker_id"] = worker_id
    if clinician_id is not None:
        updates["clinician_id"] = clinician_id
    if xray_img is not None:
        updates["xray_img"] = xray_img
    if ai_suspected is not None:
        updates["ai_suspected"] = ai_suspected
    if verified_ai is not None:
        updates["verified_ai"] = verified_ai
    if clinician_note is not None:
        updates["clinician_note"] = clinician_note
    if last_updated is not None:
        updates["last_updated"] = last_updated

    if not updates:
        return  # No updates to make

    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [patient_id]

    query = f"UPDATE patients SET {set_clause} WHERE id = ?"
    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

def get_patient(id):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
    patient = cursor.fetchone()
    
    connection.close()
    
    return patient if patient else None  