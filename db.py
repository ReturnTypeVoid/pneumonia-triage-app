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

def list_patients(search_query=None):
    # Get a connection to the database
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, address, address_2, city, state, zip, email, phone, dob, sex,
               height, weight, blood_type, smoker_status, allergies, vaccination_history,
               fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, worker_id, clinician_id
        FROM patients
    '''
    
    params = []
    
    # If search query exists, filter results
    if search_query:
        query += '''
        WHERE LOWER(first_name) LIKE ? 
           OR LOWER(surname) LIKE ?
           OR LOWER(email) LIKE ?
           OR LOWER(phone) LIKE ?
        '''
        search_pattern = f"%{search_query.lower()}%"  # Wildcard for partial match
        params = [search_pattern] * 4  # Apply search pattern to all fields

    cursor.execute(query, params)
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def list_patients_flagged_by_ai():
    connection = get_connection()
    cursor = connection.cursor()

    query = '''
        SELECT id, first_name, surname, condition, status
        FROM patients
        WHERE ai_flag = 1
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

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

def add_patient(
    first_name, surname, address, city, state, zip_code, dob, sex, height, weight, blood,
    smoker_status, alcohol, allergies, vaccination_history, fever, cough, cough_duration, 
    cough_type, chest_pain, breath, fatigue, chills, worker_id, address2=None, email=None, phone=None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO patients (
            first_name, surname, address, address_2, city, state, zip, email, phone, 
            dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, 
            allergies, vaccination_history, fever, cough, cough_duration, cough_type, 
            chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        first_name, surname, address, address2, city, state, zip_code, email, phone,
        dob, sex, height, weight, blood, smoker_status, alcohol, 
        allergies, vaccination_history, fever, cough, cough_duration, 
        cough_type, chest_pain, breath, fatigue, chills, worker_id
    ))

    connection.commit()
    connection.close()