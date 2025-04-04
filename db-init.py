import os
import sqlite3
import bcrypt

# Ensure 'database' directory exists
db_dir = 'database'
db_path = os.path.join(db_dir, 'database.db')

if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create User table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('worker', 'clinician', 'admin')),
    email TEXT,
    profile_img TEXT
);
''')

# Create Patient table
c.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    surname TEXT NOT NULL,
    address TEXT NOT NULL,
    address_2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    dob TEXT NOT NULL,
    sex TEXT NOT NULL,
    height REAL NOT NULL,
    weight REAL NOT NULL,
    blood_type TEXT NOT NULL,
    smoker_status TEXT NOT NULL,
    alcohol_consumption TEXT NOT NULL,
    allergies TEXT NOT NULL,
    vaccination_history TEXT NOT NULL,
    fever BOOLEAN NOT NULL,
    cough BOOLEAN NOT NULL,
    cough_duration INTEGER NOT NULL,
    cough_type TEXT NOT NULL,
    chest_pain BOOLEAN NOT NULL,
    shortness_of_breath BOOLEAN NOT NULL,
    fatigue BOOLEAN NOT NULL,
    chills_sweating BOOLEAN NOT NULL,
    worker_id INTEGER NOT NULL,
    clinician_id INTEGER,
    xray_img TEXT,
    ai_suspected BOOLEAN,   
    pneumonia_confirmed BOOLEAN,  
    worker_notes TEXT,
    clinician_note TEXT,
    last_updated TEXT NOT NULL,
    case_closed BOOLEAN,
    FOREIGN KEY (worker_id) REFERENCES users(id),
    FOREIGN KEY (clinician_id) REFERENCES users(id)
);
''')


# Create Settings table
c.execute('''
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twilio_account_id TEXT,
    twilio_secret_key TEXT,
    twilio_phone TEXT,
    smtp_server TEXT,
    smtp_port INTEGER,
    smtp_tls BOOLEAN,
    smtp_username TEXT,
    smtp_password TEXT,
    smtp_sender TEXT
);
''')

# Hash password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Insert admin user with hashed password
admin_password = hash_password('admin123')

c.execute('''
INSERT INTO users (name, username, password, role, email)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(username) DO NOTHING
''', ('Admin User', 'admin', admin_password, 'admin', 'admin@example.com'))

# Insert some workers and clinicians with hashed passwords
worker_password = hash_password('worker123')
clinician_password = hash_password('clinician123')

c.execute('''
INSERT INTO users (name, username, password, role, email)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(username) DO NOTHING
''', ('Worker One', 'worker', worker_password, 'worker', 'worker1@example.com'))

c.execute('''
INSERT INTO users (name, username, password, role, email)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(username) DO NOTHING
''', ('Clinician One', 'clinician', clinician_password, 'clinician', 'clinician1@example.com'))

# Patients to review
c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight,
blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration,
cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img,
ai_suspected, pneumonia_confirmed, worker_notes, clinician_note, last_updated, case_closed)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Liam', 'Hughes', '1 Elm St', 'Metro City', 'State', '11111', 'liam.h@example.com', '555-111-1111', '1988-01-01', 'Male', 175.0, 80.0,
'A+', 'No', '1-5', 'None', 'Flu', 1, 1, 2, 'Dry', 0, 0, 1, 0, 6, None, None, True, None, None, None, '2025-03-20', False))

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight,
blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration,
cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img,
ai_suspected, pneumonia_confirmed, worker_notes, clinician_note, last_updated, case_closed)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Zara', 'Clark', '2 Oak St', 'Metro City', 'State', '11112', 'zara.c@example.com', '555-111-1112', '1990-02-02', 'Female', 165.0, 60.0,
'B+', 'Yes', '0', 'Peanuts', 'Covid', 1, 1, 1, 'Wet', 0, 0, 1, 0, 6, None, None, True, None, None, None, '2025-03-21', False))

# Reviewed patients 
c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight,
blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration,
cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img,
ai_suspected, pneumonia_confirmed, worker_notes, clinician_note, last_updated, case_closed)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Noah', 'Walker', '4 Birch St', 'Lakeside', 'State', '22221', 'noah.w@example.com', '555-222-2221', '1978-04-04', 'Male', 172.0, 78.0,
'AB+', 'Yes', '15-21', 'None', 'Covid Booster', 1, 1, 4, 'Wet', 1, 1, 1, 1, 7, 9, None, True, True, None, 'Confirmed mild case', '2025-03-23', False))

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight,
blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration,
cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img,
ai_suspected, pneumonia_confirmed, worker_notes, clinician_note, last_updated, case_closed)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Ella', 'Green', '5 Maple St', 'Lakeside', 'State', '22222', 'ella.g@example.com', '555-222-2222', '1995-05-05', 'Female', 170.0, 65.0,
'O+', 'No', '0', 'None', 'Hep B', 1, 1, 2, 'Dry', 0, 0, 0, 0, 7, 10, None, True, False, None, 'False positive AI', '2025-03-24', False))

# Confirmed Pneumonia

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight,
blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration,
cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img,
ai_suspected, pneumonia_confirmed, worker_notes, clinician_note, last_updated, case_closed)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Ivy', 'Reed', '11 Pine St', 'Rivertown', 'State', '44442', 'ivy.r@example.com', '555-444-4442', '1993-11-11', 'Female', 160.0, 58.0,
'B+', 'Yes', '15-21', 'Shellfish', 'Covid Booster', 1, 1, 1, 'Wet', 1, 1, 1, 0, 6, 9, None, True, True, None, 'Stable, follow-up in 2 weeks', '2025-03-30', False))

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight,
blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration,
cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img,
ai_suspected, pneumonia_confirmed, worker_notes, clinician_note, last_updated, case_closed)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Ethan', 'Barnes', '12 Fir St', 'Rivertown', 'State', '44443', 'ethan.b@example.com', '555-444-4443', '1987-12-12', 'Male', 182.0, 88.0,
'O-', 'No', '6-14', 'None', 'Measles', 1, 1, 2, 'Dry', 0, 1, 0, 0, 6, 10, None, True, True, None, 'Confirmed via scan', '2025-03-31', False))

# Insert dummy Twilio settings
c.execute('''
INSERT INTO settings (twilio_account_id, twilio_secret_key, twilio_phone)
VALUES (?, ?, ?)
ON CONFLICT(id) DO NOTHING
''', ('dummy_account_id', 'dummy_secret_key', '+1234567890'))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Sample database setup completed with sample data.")
print("Login with admin/admin123, worker/worker123, or clinician/clinician123")
