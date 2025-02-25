import sqlite3
import bcrypt

# Connect to SQLite database
conn = sqlite3.connect('database/database.db')
c = conn.cursor()

# Create User table
c.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('worker', 'clinician', 'admin')),
    email TEXT
);
''')

# Create Patient table
c.execute('''
CREATE TABLE IF NOT EXISTS patient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    surname TEXT NOT NULL,
    address TEXT,
    address_2 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    email TEXT,
    phone TEXT,
    dob TEXT,
    sex TEXT,
    height REAL,
    weight REAL,
    blood_type TEXT,
    smoker_status TEXT,
    allergies TEXT,
    vaccination_history TEXT,
    fever BOOLEAN,
    cough BOOLEAN,
    cough_duration INTEGER,
    cough_type TEXT,
    chest_pain BOOLEAN,
    shortness_of_breath BOOLEAN,
    fatigue BOOLEAN,
    worker_id INTEGER NOT NULL,
    clinician_id INTEGER,
    FOREIGN KEY (worker_id) REFERENCES user(id),
    FOREIGN KEY (clinician_id) REFERENCES user(id)
);
''')

# Hash password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Insert admin user with hashed password
admin_password = hash_password('admin123')  # Example password for admin
c.execute('''
INSERT INTO user (name, username, password, role, email)
VALUES (?, ?, ?, ?, ?)
''', ('Admin User', 'admin', admin_password, 'admin', 'admin@example.com'))

# Insert some workers and clinicians with hashed passwords
worker_password = hash_password('worker123')
clinician_password = hash_password('clinician123')

c.execute('''
INSERT INTO user (name, username, password, role, email)
VALUES (?, ?, ?, ?, ?)
''', ('Worker One', 'worker', worker_password, 'worker', 'worker1@example.com'))

c.execute('''
INSERT INTO user (name, username, password, role, email)
VALUES (?, ?, ?, ?, ?)
''', ('Clinician One', 'clinician', clinician_password, 'clinician', 'clinician1@example.com'))

# Insert some sample patients
c.execute('''
INSERT INTO patient (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, fever, cough, worker_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('John', 'Doe', '123 Main St', 'Cityville', 'State', '12345', 'john.doe@example.com', '555-555-5555', '1990-01-01', 'M', 180.5, 75.2, 'O+', 1, 1, 1))

c.execute('''
INSERT INTO patient (first_name, surname, address, city, state, zip, email, phone, dob, sex, height, weight, blood_type, fever, cough, worker_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Jane', 'Smith', '456 Oak Rd', 'Townsville', 'State', '67890', 'jane.smith@example.com', '555-555-1234', '1985-05-05', 'F', 160.2, 65.3, 'A+', 1, 0, 1))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Sample database setup completed with sample data.")
print("Login with admin/admin123, worker/worker123, or clinician/clinician123")
