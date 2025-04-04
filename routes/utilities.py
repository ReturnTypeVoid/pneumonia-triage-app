import os, uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, request, render_template, redirect, url_for
from routes.auth import get_user_from_token, check_is_clinician, check_is_worker, check_jwt_tokens
from db import update_user_image, get_user_image, update_xray_image, get_xray_image, get_patient, delete_xray_image, get_settings, get_user

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

@utilities.route('/users/avatar/upload', methods=['POST'])
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


@utilities.route('/patients/xray/upload/<int:id>', methods=['POST'])
def upload_xray(id):
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

@utilities.route('/patients/xray/delete/<int:id>', methods=['POST'])
def delete_xray(id):
    
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response  

    
    if not (check_is_worker(user_data) or check_is_clinician(user_data)):
        return response  

    
    patient = get_patient(id)
    if not patient or not patient['xray_img']:  
        return redirect(url_for('patients.edit_patient', id=id))

    
    delete_xray_image(id)  

    return redirect(url_for('patients.edit_patient', id=id))

@utilities.route('/send-email/<int:patient_id>', methods=['POST'])
def send_email(patient_id):
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response  

    if not (check_is_worker(user_data) or check_is_clinician(user_data)):
        return response  

    settings = get_settings()

    if not settings:
        return "SMTP settings not found", 500  # Return a proper HTTP error

    smtp_settings = {
        "smtp_server": settings["smtp_server"],
        "smtp_port": settings["smtp_port"],
        "smtp_tls": settings["smtp_tls"],
        "smtp_username": settings["smtp_username"],
        "smtp_password": settings["smtp_password"],
        "smtp_sender": settings["smtp_sender"]
    }

    current_user = get_user_from_token()["username"]
    patient = get_patient(patient_id)
    worker = get_user(current_user)

    if not patient or not worker:
        return {"error": "Patient or worker not found"}, 404

    patient_name = f"{patient['first_name']} {patient['surname']}"
    worker_name = worker["name"]
    
    recipient_email = patient["email"] # Change this to an actual email address for real world testing.
    subject = "X-ray Test Results"
    body = f"""Hello {patient_name},

Your chest x-ray results are now available. Please visit your local clinic at your earliest convenience.

Best regards,
{worker_name}
"""

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_settings["smtp_sender"]
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_settings["smtp_server"], smtp_settings["smtp_port"])
        
        if smtp_settings["smtp_tls"]:
            server.starttls()  

        server.login(smtp_settings["smtp_username"], smtp_settings["smtp_password"])
        
        server.sendmail(smtp_settings["smtp_sender"], recipient_email, msg.as_string())

        server.quit()

        return {"message": "Email sent successfully"}, 200

    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}, 500


