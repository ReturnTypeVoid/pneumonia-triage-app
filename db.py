import sqlite3

def get_connection():
    """
    Get a database connection.

    Description:
        Opens a connection to the SQLite database and sets up row access by column name.

    Arguments:
        None

    Returns:
        sqlite3.Connection: Database connection object.

    Author
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = sqlite3.connect('database/database.db')
    connection.row_factory = sqlite3.Row  
    return connection

def get_users():
    """
    Get all users.

    Description:
        Fetches a list of all users with their basic info (ID, name, username, role).

    Arguments:
        None

    Returns:
        list: List of user rows.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, name, username, role FROM users')

    users = cursor.fetchall()  
    connection.close()  

    return users

def get_user(username):
    """
    Get user by username.

    Description:
        Looks up a user in the database using their username.

    Arguments:
        username (str): The username to look up.

    Returns:
        sqlite3.Row or None: User row if found, otherwise None.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

    user = cursor.fetchone()
    connection.close()
    
    return user

def get_user_id(username):
    """
    Get user ID from username.

    Description:
        Returns the ID of a user based on their username.

    Arguments:
        username (str): Username to search.

    Returns:
        int or None: User ID if found.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    
    connection.close()
    
    return user_id[0] if user_id else None  

def check_user_exists(username):
    """
    Check if a user exists.

    Description:
        Checks the database to see if a user with the given username exists.

    Arguments:
        username (str): Username to check.

    Returns:
        bool: True if the user exists, False otherwise.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    return get_user(username) is not None

def add_user(name, username, password, role, email):
    """
    Add a new user.

    Description:
        Inserts a new user record. Does nothing if username already exists.

    Arguments:
        name, username, password, role, email

    Returns:
        bool: True if the user was added.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO users (name, username, password, role, email)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username) DO NOTHING
    ''', (name, username.lower(), password, role, email))  

    connection.commit()
    connection.close()

    return True

def update_user(username, new_username=None, name=None, password=None, role=None, email=None):
    """
    Update user fields.

    Description:
        Updates selected fields for a user. Skips any values not provided.

    Arguments:
        username (str): Current username.
        new_username, name, password, role, email (optional)

    Returns:
        bool: True if update was successful.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    updates = {}
    if new_username:
        updates["username"] = new_username.lower()  
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
    values = list(updates.values()) + [username.lower()]  

    query = f"UPDATE users SET {set_clause} WHERE username = ?"

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return True

def delete_user(username):
    """
    Delete a user.

    Description:
        Removes a user from the database by their username.

    Arguments:
        username (str): Username to delete.

    Returns:
        bool: True if user was deleted.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE from users WHERE username =?", (username,))

    connection.commit()
    connection.close()

    return True

def get_settings():
    """
    Get current system settings.

    Description:
        Loads the current settings record from the database.

    Arguments:
        None

    Returns:
        dict or None: Settings record.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM settings WHERE id = 1;')
    settings = cursor.fetchone()
    
    connection.close()

    return settings

def update_twilio_settings(twilio_account_id=None, twilio_secret_key=None, twilio_phone=None):
    """
    Update Twilio settings.

    Description:
        Saves Twilio credentials to the database.

    Arguments:
        twilio_account_id, twilio_secret_key, twilio_phone

    Returns:
        bool: True if updated.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

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
        return  

    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [1]  

    query = f"UPDATE settings SET {set_clause} WHERE id = ?"
    
    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return True

def update_smtp_settings(smtp_server=None, smtp_port=None, smtp_tls=None, smtp_username=None, smtp_password=None, smtp_sender=None):
    """
    Update SMTP settings.

    Description:
        Updates or replaces the app’s email server settings.

    Arguments:
        smtp_server, smtp_port, smtp_tls, smtp_username, smtp_password, smtp_sender

    Returns:
        bool: True if saved.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    
    cursor.execute('''
        INSERT OR REPLACE INTO settings 
        (id, smtp_server, smtp_port, smtp_tls, smtp_username, smtp_password, smtp_sender)
        VALUES (
            1,  -- Hardcode ID since we only have one settings entry
            COALESCE(?, (SELECT smtp_server FROM settings WHERE id=1)),
            COALESCE(?, (SELECT smtp_port FROM settings WHERE id=1)),
            COALESCE(?, (SELECT smtp_tls FROM settings WHERE id=1)),
            COALESCE(?, (SELECT smtp_username FROM settings WHERE id=1)),
            COALESCE(?, (SELECT smtp_password FROM settings WHERE id=1)),
            COALESCE(?, (SELECT smtp_sender FROM settings WHERE id=1))
        )
    ''', (
        smtp_server,
        smtp_port,
        smtp_tls,
        smtp_username,
        smtp_password,
        smtp_sender
    ))

    connection.commit()
    connection.close()

    return True

def update_user_image(username, profile_img):
    """
    Update profile image for a user.

    Description:
        Saves the profile image filename for a user.

    Arguments:
        username (str), profile_img (str)

    Returns:
        bool: True if updated.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE users SET profile_img = ? WHERE username = ?", (profile_img, username))

    connection.commit()
    cursor.close()
    connection.close()

    return True

def update_xray_image(id, xray_img):
    """
    Save an x-ray image for a patient.

    Description:
        Updates the patient's record with the new x-ray filename.

    Arguments:
        id (int): Patient ID.
        xray_img (str): Filename.

    Returns:
        bool: True if updated.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE patients SET xray_img = ? WHERE id = ?", (xray_img, id))

    connection.commit()
    cursor.close()
    connection.close()

    return True

def get_user_image(username):
    """
    Get profile image filename for a user.

    Description:
        Returns the image filename for a user’s avatar.

    Arguments:
        username (str)

    Returns:
        str or None: Image filename.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT profile_img FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0] if result else None

def delete_user_image(id):
    """
    Clear profile image for a patient.

    Description:
        Removes the profile image reference in the database.

    Arguments:
        id (int): Patient ID.

    Returns:
        bool: True if cleared.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE patients SET profile_img = NULL WHERE id = ?", (id,))
    connection.commit()

    cursor.close()
    connection.close()

    return True

def get_xray_image(id):
    """
    Get x-ray image filename.

    Description:
        Looks up a patient’s x-ray image.

    Arguments:
        id (int): Patient ID.

    Returns:
        str or None: Image filename.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT xray_img FROM patients WHERE id = ?", (id,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0] if result else None

def delete_xray_image(id):
    """
    Clear x-ray image from a patient record.

    Description:
        Sets the x-ray image field to NULL.

    Arguments:
        id (int): Patient ID.

    Returns:
        None

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE patients SET xray_img = NULL WHERE id = ?", (id,))
    connection.commit()

    cursor.close()
    connection.close()

def list_patients(search_query=None):
    """
    List all active patients.

    Description:
        Fetches patient records that are not marked as closed.
        Supports optional search by name, contact, and notes.

    Arguments:
        search_query (str, optional): Filter string.

    Returns:
        list: Patient records matching the query.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, email, phone, dob, allergies, vaccination_history,
               clinician_id, last_updated, clinician_note, xray_img
        FROM patients
        WHERE (case_closed IS NULL OR case_closed != TRUE)
    '''
    
    params = []

    if search_query:
        query += '''
        AND (
            LOWER(first_name) LIKE ? 
            OR LOWER(surname) LIKE ?
            OR LOWER(email) LIKE ?
            OR LOWER(phone) LIKE ?
            OR LOWER(dob) LIKE ?
            OR LOWER(allergies) LIKE ?
            OR LOWER(vaccination_history) LIKE ?
            OR LOWER(last_updated) LIKE ?
            OR LOWER(clinician_note) LIKE ?
        )
        '''
        search_pattern = f"%{search_query.lower()}%"
        params = [search_pattern] * 9

    query += " ORDER BY last_updated ASC"

    cursor.execute(query, params)
    patients = cursor.fetchall()
    connection.close()

    return patients

def patient_list_ai_detect():
    """
    List patients flagged by AI.

    Description:
        Returns a list of patients where AI suspected pneumonia
        but they haven't been reviewed yet.

    Arguments:
        None

    Returns:
        list: Processed patient records with human-readable status.

    Author:
        Amina Asghar (CodeBrainZero)
    """


    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, pneumonia_confirmed
        FROM patients
        WHERE ai_suspected = TRUE
        AND pneumonia_confirmed IS NULL
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()

    
    patient_list = []
    for row in rows:
        patient_dict = dict(row)
        
        
        if patient_dict['ai_suspected']:
            patient_dict['status'] = 'Pneumonia'
        else:
            patient_dict['status'] = 'No issues detected'

        
        if patient_dict['pneumonia_confirmed'] is None:
            patient_dict['condition'] = 'Pending Review'
        elif patient_dict['pneumonia_confirmed']:
            patient_dict['condition'] = 'Confirmed Pneumonia'
        else:
            patient_dict['condition'] = 'Not Pneumonia'

        
        
        
        
        patient_list.append(patient_dict)

    return patient_list

def add_patient(first_name, surname, address, city, 
                state, zip, dob, sex, height, 
                weight, blood_type, smoker_status, alcohol_consumption, 
                allergies, vaccination_history, fever, cough, 
                chest_pain, shortness_of_breath, fatigue, 
                chills_sweating, last_updated, worker_id, 
                address_2=None, email=None, phone=None, 
                cough_duration=None, cough_type=None, worker_notes=None):
    """
    Add a new patient record.

    Description:
        Saves a new patient to the database with full history, symptoms,
        contact info, and optional metadata.

    Arguments:
        All expected patient form fields.

    Returns:
        bool: True if patient was added.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO patients (
            first_name, surname, address, city, state, zip, dob, sex, height, 
            weight, blood_type, smoker_status, alcohol_consumption, allergies, 
            vaccination_history, fever, cough, chest_pain, shortness_of_breath,
            fatigue, chills_sweating, last_updated, worker_id, address_2, email, 
            phone, cough_duration, cough_type, worker_notes, ai_suspected, pneumonia_confirmed
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        first_name, surname, address, city, state, zip, dob, sex, height, 
        weight, blood_type, smoker_status, alcohol_consumption, allergies, 
        vaccination_history, fever, cough, chest_pain, shortness_of_breath, 
        fatigue, chills_sweating, last_updated, worker_id, 
        address_2 if address_2 is not None else None, 
        email if email is not None else None, 
        phone if phone is not None else None, 
        cough_duration if cough_duration is not None else None, 
        cough_type if cough_type is not None else None,
        worker_notes if worker_notes is not None else None, None, None
    ))

    connection.commit()
    connection.close()

    return True

def patients_to_review(search_query=None):
    """
    List patients waiting for clinician review.

    Description:
        Returns patients marked for review by a clinician.
        Supports optional filtering by name or notes.

    Arguments:
        search_query (str, optional)

    Returns:
        list: Filtered patient records.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()

    base_query = '''
        SELECT id, first_name, surname, ai_suspected, pneumonia_confirmed, clinician_note, xray_img
        FROM patients
        WHERE clinician_to_review = TRUE
    '''

    params = []

    if search_query:
        base_query += '''
            AND (
                LOWER(first_name) LIKE ?
                OR LOWER(surname) LIKE ?
                OR LOWER(clinician_note) LIKE ?
            )
        '''
        search_pattern = f"%{search_query.lower()}%"
        params = [search_pattern] * 3

    base_query += " ORDER BY last_updated ASC"

    cursor.execute(base_query, params)
    patients = cursor.fetchall()
    connection.close()

    return patients

def reviewed_patients(search_query=None):
    """
    List patients already reviewed by a clinician.

    Description:
        Returns patients that have been marked as reviewed.
        Can be filtered by search query.

    Arguments:
        search_query (str, optional)

    Returns:
        list: Reviewed patient records.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, pneumonia_confirmed, clinician_note, xray_img
        FROM patients
        WHERE clinician_to_review = FALSE
            AND clinician_reviewed = TRUE
    '''

    params = []

    if search_query:
        query += '''
            AND (
                LOWER(first_name) LIKE ?
                OR LOWER(surname) LIKE ?
                OR LOWER(clinician_note) LIKE ?
            )
        '''
        search_pattern = f"%{search_query.lower()}%"
        params = [search_pattern] * 3

    query += " ORDER BY last_updated ASC"

    cursor.execute(query, params)
    patients = cursor.fetchall()
    connection.close()

    return patients

def all_pneumonia_cases(search_query=None):
    """
    Get all confirmed pneumonia cases.

    Description:
        Returns patients with confirmed pneumonia that aren’t closed yet.
        Optionally filtered by search string.

    Arguments:
        search_query (str, optional)

    Returns:
        list: Filtered patient records.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, pneumonia_confirmed, clinician_note, xray_img
        FROM patients
        WHERE pneumonia_confirmed = TRUE 
            AND (case_closed IS NULL OR case_closed = FALSE)
    '''

    params = []

    if search_query:
        query += '''
            AND (
                LOWER(first_name) LIKE ?
                OR LOWER(surname) LIKE ?
                OR LOWER(clinician_note) LIKE ?
            )
        '''
        search_pattern = f"%{search_query.lower()}%"
        params = [search_pattern] * 3

    query += " ORDER BY last_updated ASC"

    cursor.execute(query, params)
    patients = cursor.fetchall()
    connection.close()

    return patients

def get_closed_cases(search_query=None):
    """
    Get all closed patient cases.

    Description:
        Loads patients where the case_closed flag is set to TRUE.
        Supports optional search by name or notes.

    Arguments:
        search_query (str, optional)

    Returns:
        list: Closed case records.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, ai_suspected, pneumonia_confirmed, clinician_note, xray_img
        FROM patients
        WHERE case_closed = TRUE
    '''

    params = []

    if search_query:
        query += '''
            AND (
                LOWER(first_name) LIKE ?
                OR LOWER(surname) LIKE ?
                OR LOWER(clinician_note) LIKE ?
            )
        '''
        search_pattern = f"%{search_query.lower()}%"
        params = [search_pattern] * 3

    query += " ORDER BY last_updated DESC"

    cursor.execute(query, params)
    patients = cursor.fetchall()
    connection.close()

    return patients

def close_patient_case(patient_id):
    """
    Mark a patient case as closed.

    Description:
        Sets case_closed to TRUE and updates the timestamp.

    Arguments:
        patient_id (int): The ID of the patient.

    Returns:
        bool: True if successful.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('''
            UPDATE patients
            SET case_closed = TRUE,
                last_updated = datetime('now')
            WHERE id = ?
        ''', (patient_id,))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error closing patient case: {e}")
        return False
    finally:
        connection.close()

def reopen_patient_case(patient_id):
    """
    Reopen a previously closed patient case.

    Description:
        Sets case_closed to FALSE and updates the timestamp.

    Arguments:
        patient_id (int)

    Returns:
        bool: True if successful.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('''
            UPDATE patients
            SET case_closed = FALSE,
                last_updated = datetime('now')
            WHERE id = ?
        ''', (patient_id,))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error reopening patient case: {e}")
        return False
    finally:
        connection.close()

def delete_patient(patient_id):
    """
    Delete a patient record.

    Description:
        Removes a patient from the database by ID.

    Arguments:
        patient_id (int)

    Returns:
        bool: True if deleted.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))

    connection.commit()
    connection.close()

    return True

def update_patient(patient_id, first_name=None, surname=None, address=None, address_2=None, city=None, 
                   state=None, zip=None, email=None, phone=None, dob=None, sex=None, height=None, 
                   weight=None, blood_type=None, smoker_status=None, alcohol_consumption=None, 
                   allergies=None, vaccination_history=None, fever=None, cough=None, cough_duration=None, 
                   cough_type=None, chest_pain=None, shortness_of_breath=None, fatigue=None, 
                   chills_sweating=None, worker_id=None, clinician_id=None, xray_img=None, 
                   ai_suspected=None, pneumonia_confirmed=None, clinician_note=None, 
                   worker_notes=None, last_updated=None):
    """
    Update fields for a patient.

    Description:
        Updates any combination of patient fields. Skips any that are not provided.

    Arguments:
        patient_id (int): The patient’s ID.
        Other optional patient fields.

    Returns:
        bool: True if the update was applied.

    Author:
        Amina Asghar (CodeBrainZero)
    """

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
    if pneumonia_confirmed is not None:
        updates["pneumonia_confirmed"] = pneumonia_confirmed
    if clinician_note is not None:
        updates["clinician_note"] = clinician_note
    if worker_notes is not None:
        updates["worker_notes"] = worker_notes
    if last_updated is not None:
        updates["last_updated"] = last_updated

    if not updates:
        return  

    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [patient_id]

    query = f"UPDATE patients SET {set_clause} WHERE id = ?"
    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return True

def get_patient(id):
    """
    Get a single patient by ID.

    Description:
        Fetches all available fields for one patient.

    Arguments:
        id (int): The patient's ID.

    Returns:
        dict or None: Patient record if found.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
    patient = cursor.fetchone()
    
    connection.close()
    
    return patient if patient else None  

def list_closed_cases():
    """
    Get a list of closed cases for display.

    Description:
        Loads patients with case_closed set to 1, sorted by last update time.

    Arguments:
        None

    Returns:
        list: Closed patient records.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, email, phone, dob, allergies, vaccination_history, clinician_id, last_updated, clinician_note, xray_img
        FROM patients
        WHERE case_closed = 1
        ORDER BY last_updated DESC
    '''

    cursor.execute(query)
    patients = cursor.fetchall()
    connection.close()

    return patients

def get_reviewed_cases_for_worker(search_query=None):
    """
    Get reviewed cases needing worker follow-up.

    Description:
        Returns patients with confirmed results and notes,
        but not yet closed. Supports optional search.

    Arguments:
        search_query (str, optional)

    Returns:
        list: Patient records.

    Author:
        Amina Asghar (CodeBrainZero)
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT * FROM patients
        WHERE pneumonia_confirmed IS NOT NULL
        AND clinician_note IS NOT NULL
        AND clinician_note != ''
        AND case_closed IS NOT TRUE
    '''
    params = []
    
    if search_query:
        query += '''
            AND (LOWER(first_name) LIKE ? 
            OR LOWER(surname) LIKE ? 
            OR LOWER(clinician_note) LIKE ?)
        '''
        search_pattern = f"%{search_query.lower()}%"
        params = [search_pattern, search_pattern, search_pattern]

    cursor.execute(query, params)
    cases = cursor.fetchall()
    connection.close()
    return cases

def update_ai_suspected(patient_id, prediction):
    """
    Update AI-predicted status for a patient.

    Description:
        Sets the ai_suspected flag based on the prediction result.

    Arguments:
        patient_id (int), prediction (str): "Pneumonia" or "Normal"

    Returns:
        None

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    conn = get_connection()
    cursor = conn.cursor()

    ai_suspected = 1 if prediction == "Pneumonia" else 0

    cursor.execute(
        "UPDATE patients SET ai_suspected = ? WHERE id = ?",
        (ai_suspected, patient_id)
    )

    conn.commit()
    conn.close()

def update_clinician_to_review(patient_id, value):
    """
    Set a patient to be reviewed by a clinician.

    Description:
        Updates the clinician_to_review flag.

    Arguments:
        patient_id (int), value (int): 1 or 0

    Returns:
        None

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE patients SET clinician_to_review = ? WHERE id = ?",
        (value, patient_id)
    )

    conn.commit()
    conn.close()

def update_clinician_reviewed(patient_id, value):
    """
    Set a patient as reviewed by a clinician.

    Description:
        Updates the clinician_reviewed flag.

    Arguments:
        patient_id (int), value (int): 1 or 0

    Returns:
        None

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE patients SET clinician_reviewed = ? WHERE id = ?",
        (value, patient_id)
    )

    conn.commit()
    conn.close()
