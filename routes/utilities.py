import os, uuid
from flask import Blueprint, request, render_template, redirect, url_for
from routes.auth import get_user_from_token
from db import update_user_image, get_user, get_user_image, update_xray_image, get_xray_image, get_patient

utilities = Blueprint('utilities', __name__)

AVATAR_FOLDER = "static/images/avatars"
XRAY_FOLDER = "static/images/xrays"


os.makedirs(AVATAR_FOLDER, exist_ok=True)
os.makedirs(XRAY_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder):
    unique_filename = f"{uuid.uuid4().hex}.jpg"
    save_path = os.path.join(folder, unique_filename)
    file.save(save_path)
    return unique_filename, save_path

@utilities.route('/upload/avatar', methods=['POST'])
def upload_avatar():
    current_user = get_user_from_token()['username']

    if 'file' not in request.files:
        return redirect(url_for('profile.view_profile'))

    file = request.files['file']

    if not allowed_file(file.filename):
        return redirect(url_for('profile.view_profile'))


    
    existing_image = get_user_image(current_user)

    
    if existing_image:
        old_image_path = os.path.join(AVATAR_FOLDER, existing_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

    
    filename, path = save_file(file, AVATAR_FOLDER)

    
    update_user_image(current_user, filename)

    return redirect(url_for('profile.view_profile'))


@utilities.route('/upload/xray/<id>', methods=['POST'])
def upload_xray(id):
    current_user = get_user_from_token()['username']
    patient = get_patient(id)

    if 'file' not in request.files:
        return redirect(url_for('patients.edit_patient', id=patient['id']))

    file = request.files['file']

    if not allowed_file(file.filename):
        return redirect(url_for('patients.edit_patient', id=patient['id']))


    
    existing_image = get_xray_image(patient['id'])

    
    if existing_image:
        old_image_path = os.path.join(XRAY_FOLDER, existing_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

    
    filename, path = save_file(file, XRAY_FOLDER)

    
    update_xray_image(patient['id'], filename)

    return redirect(url_for('patients.edit_patient', id=patient['id']))

