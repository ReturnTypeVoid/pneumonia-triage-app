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
    clinician_to_review BOOLEAN,
    clinician_reviewed BOOLEAN,
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



# First create the table
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

# Then insert initial data in a separate operation
c.execute('''
INSERT INTO settings (
    twilio_account_id,
    twilio_secret_key,
    twilio_phone,
    smtp_server,
    smtp_port,
    smtp_tls,
    smtp_username,
    smtp_password,
    smtp_sender
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO NOTHING
''', (
    'dummy_account_id',
    'dummy_secret_key',
    '+1234567890',
    'smtp.example.com',
    587,
    1,
    'your_email@example.com',
    'your_password',
    'Clinic Alerts <noreply@example.com>'
))

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
