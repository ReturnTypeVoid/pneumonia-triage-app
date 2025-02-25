from flask import Flask, render_template, redirect, url_for, flash, request
from routes.auth import login, logout, is_authenticated
from routes.admin import list_users
from routes.worker import list_patients
app = Flask(__name__)

app.config['SECRET_KEY'] = 'super_secret_key' # For the love of all things, change this.

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_route(): # Comment continuation - this method is either GET or POST. GET will render the login page for people, POST will submit the login creds, check against db, and authenticate if creds are valid
    return login()

@app.route('/logout')
def logout_route(): 
    return logout()

@app.route('/admin/dashboard')
def admin_dashboard():
    return list_users()

@app.route('/worker/dashboard')
def worker_dashboard():
    return list_patients()

if __name__ == '__main__':
    app.run(debug=True) # Allows for on-the-fly reloads without having to stop/start the app. Commented by Reece, 24/02/2025 @22:46 GMT
