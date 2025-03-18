import os, uuid
from flask import Blueprint, request, render_template, redirect, url_for
from routes.auth import get_user_from_token
from db import update_user_image, get_user, get_user_image

utilities = Blueprint('utilities', __name__)

AVATAR_FOLDER = "static/images/avatars"
XRAY_FOLDER = "static/images/xrays"

# Ensure directories exist
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


    # Get current profile image
    existing_image = get_user_image(current_user)

    # Delete old image if it exists
    if existing_image:
        old_image_path = os.path.join(AVATAR_FOLDER, existing_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

    # Upload new image
    filename, path = save_file(file, AVATAR_FOLDER)

    # Update the database with the new image filename
    update_user_image(current_user, filename)

    return redirect(url_for('profile.view_profile'))
