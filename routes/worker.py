from flask import Blueprint, request, render_template
from routes.auth import check_jwt_tokens, check_is_worker, get_user_from_token 
from db import list_patients, get_user  

worker = Blueprint('worker', __name__)

@worker.route('/dashboard')
def dashboard():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response
    
    current_user = get_user_from_token()['username']

    return render_template('worker/dashboard.html', current_user=get_user(current_user), patients=list_patients())
