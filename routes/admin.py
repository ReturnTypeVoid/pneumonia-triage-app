from flask import Blueprint, render_template
from routes.auth import check_jwt_tokens, check_is_admin, get_user_from_token
from db import get_users, get_user

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
def dashboard():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    is_admin, response = check_is_admin(user_data)
    if not is_admin:
        return response

    current_user = get_user_from_token()['username']
    
    return render_template('admin/user_list.html', current_user=get_user(current_user), users=get_users())