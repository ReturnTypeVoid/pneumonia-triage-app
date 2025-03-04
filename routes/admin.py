from flask import Blueprint, request, render_template
import bcrypt
from routes.auth import check_jwt_tokens, check_is_admin 
from db import check_user_exists, add_user, list_users, delete_user

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
def dashboard():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_admin(user_data)
    if not user_data:
        return response

    return render_template('admin/dashboard.html', users=list_users())


@admin.route('/admin/user/create', methods=['GET', 'POST'])
def add_new_user():
    user_data, response = check_jwt_tokens()  # Verify authentication
    if not user_data:
        return response  # Redirect to login if JWT is invalid

    is_admin, response = check_is_admin(user_data)  # Verify admin access
    if not is_admin:
        return response  # Redirect if not an admin

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
        role = request.form.get('role')
        email = request.form.get('email')

        if check_user_exists(username):
            return render_template('admin/user_form.html', error="Username already exists.")

        add_user(name, username, password, role, email)

        return '''
            <script>
                window.opener.location.reload();  // Refresh the admin page
                window.close();  // Close the popup
            </script>
        '''

    return render_template('admin/user_form.html')


@admin.route('/admin/user/delete/<username>', methods=['POST'])
def delete_existing_user(username):
    user_data, response = check_jwt_tokens()  # Verify authentication
    if not user_data:
        return response  # Redirect to login if JWT is invalid

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response
    
    delete_user(username)
    

    return render_template('admin/dashboard.html', users=list_users())
