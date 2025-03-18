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
    verified_ai BOOLEAN,  
    clinician_note TEXT,    
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

#patients to review
c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img, ai_suspected, verified_ai, clinician_note)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Mark', 'Anderson', '101 Elm St', 'Metro City', 'State', '56789', 'mark.a@example.com', '555-111-2233', '1985-04-10', 'Male', 178.0, 82.0, 'A-', 'No', 'Occasionally', 'None', 'Flu Vaccine', 1, 1, 5, 'Dry', 1, 1, 1, 0, 6, None, None, True, None, None))

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img, ai_suspected, verified_ai, clinician_note)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Emily', 'Davis', '202 Oak St', 'Lakeside', 'State', '67891', 'emily.d@example.com', '555-222-3344', '1992-07-15', 'Female', 165.3, 60.2, 'B+', 'Yes', 'Rarely', 'Peanuts', 'Covid Vaccine', 1, 1, 3, 'Wet', 0, 0, 1, 1, 7, None, None, True, None, ''))

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img, ai_suspected, verified_ai, clinician_note)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Daniel', 'Garcia', '303 Pine St', 'Hilltown', 'State', '78912', 'daniel.g@example.com', '555-333-4455', '1980-02-20', 'Male', 172.5, 75.8, 'O-', 'No', 'Occasionally', 'Shellfish', 'Tetanus Shot', 1, 1, 6, 'Dry', 1, 1, 1, 0, 8, None, None, True, None, None))

#reviewed patients
c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img, ai_suspected, verified_ai, clinician_note)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Sophia', 'Martinez', '404 Birch St', 'Rivertown', 'State', '89123', 'sophia.m@example.com', '555-444-5566', '1990-10-05', 'Female', 168.0, 68.5, 'AB+', 'No', 'Regularly', 'None', 'Covid Booster', 1, 1, 4, 'Wet', 0, 0, 1, 1, 9, None, None, True, True, 'Confirmed pneumonia, treatment started'))

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img, ai_suspected, verified_ai, clinician_note)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('William', 'Johnson', '505 Willow St', 'Greenville', 'State', '91234', 'william.j@example.com', '555-555-6677', '1983-12-30', 'Male', 174.0, 80.1, 'A+', 'Yes', 'Occasionally', 'Dust', 'Flu Vaccine', 1, 1, 5, 'Dry', 1, 1, 1, 0, 10, None, None, True, False, 'False positive, no pneumonia detected'))

c.execute('''
INSERT INTO patients (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, smoker_status, alcohol_consumption, allergies, vaccination_history, fever, cough, cough_duration, cough_type, chest_pain, shortness_of_breath, fatigue, chills_sweating, worker_id, clinician_id, xray_img, ai_suspected, verified_ai, clinician_note)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Olivia', 'Brown', '606 Cedar St', 'Lakeview', 'State', '34567', 'olivia.b@example.com', '555-666-7788', '1975-08-18', 'Female', 160.2, 70.3, 'O+', 'No', 'Rarely', 'Latex', 'Hepatitis B', 1, 1, 6, 'Wet', 1, 1, 1, 1, 11, None, None, True, True, 'Severe case, hospitalization recommended'))



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
