from flask import request, render_template, redirect, url_for, session
import sqlite3
import bcrypt
from db import get_db_connection  # import db function

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Use the imported function to get the DB connection - maneas we don't have to manually put in db location every time. - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, password, role FROM user WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()  # don't forget to close the connection

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):  # Check password against hash in db
            session['user_id'] = user[0]  # Store user id in session - horrific from a security perspective, but is not important right now, and can change at the end if we have time to something like JWT - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT

            # Check the user role and redirect accordingly
            if user[2] == 'admin':  # user[2] is the role column
                return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
            elif user[2] == 'clinician':
                return redirect(url_for('clinician_dashboard'))  # Redirect to the clinician dashboard
            else:
                return redirect(url_for('worker_dashboard'))  # Redirect to the worker dashboard
        else:
            return render_template('login.html', error='Invalid username or password'), 401 # don't like this, would prefer to use Flask flash message, but not important right now. - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT

    return render_template('login.html')  # Render login form for GET requests

def logout():
    """Logs the user out by removing the user_id from the session."""
    session.pop('user_id', None)  # Remove user_id from session (logs out the user) - really awful way of doing it, but again not important right now. It's functional and that's what we need - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT
    return redirect(url_for('login_route'))  # Redirect user back to the login page

def is_authenticated():
    """Checks if the user is authenticated (i.e., logged in)."""
    return 'user_id' in session