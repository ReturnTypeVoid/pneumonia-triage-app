from flask import render_template
from db import get_db_connection  # import db function - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT

def list_users():
    # Connect to the database
    conn = get_db_connection()
    c = conn.cursor()

    # sql query, storing the returned data in users var - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT
    c.execute('SELECT id, username, role FROM user')
    users = c.fetchall()  

    conn.close()  # Close the database connection - Should ALWAYS close when finished - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT

    # Pass the users data to the template
    return render_template('admin/dashboard.html', users=users)
