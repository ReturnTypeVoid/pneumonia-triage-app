from flask import Blueprint, request, render_template
from routes.auth import check_jwt_tokens, check_is_worker
from db import list_patients

worker = Blueprint('worker', __name__)

@worker.route('/dashboard')
def dashboard():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response

    return render_template('worker/dashboard.html', patients=list_patients())
