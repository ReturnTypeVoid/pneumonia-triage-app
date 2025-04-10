import os, uuid
import smtplib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, request, redirect, url_for, flash, session
from routes.auth import get_user_from_token, check_is_clinician, check_is_worker, check_jwt_tokens
from db import update_user_image, get_user_image, update_xray_image, get_xray_image, get_patient, delete_xray_image, get_settings, get_user, update_ai_suspected, update_clinician_to_review

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

    success = update_user_image(current_user, filename)
    
    session.pop('_flashes', None)

    if success:
        flash("User avatar updated.", "success")
    else:
        flash("Failed to update user avatar.", "error")
    return redirect(url_for('profile.view_profile'))

@utilities.route('/patients/xray/upload/<int:id>', methods=['POST'])
def upload_xray(id):
    patient = get_patient(id)

    if 'file' not in request.files:
        return redirect(url_for('patients.edit_patient', id=patient['id']))

    file = request.files['file']

    if not allowed_file(file.filename):
        return redirect(url_for('patients.edit_patient', id=patient['id']))

    # Remove existing X-ray if present
    existing_image = get_xray_image(patient['id'])
    if existing_image:
        old_image_path = os.path.join(XRAY_FOLDER, existing_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
            delete_xray_image(id)

    # Save the new file
    filename, path = save_file(file, XRAY_FOLDER)
    success = update_xray_image(patient['id'], filename)

    # Predict using Tahas Keras model
    try:
        model_path = 'machine-learning/final_pneumonia_model.keras'
        model = load_model(model_path)

        image = load_img(path, target_size=(64, 64), color_mode='grayscale')
        image = img_to_array(image) / 255.0
        image = np.expand_dims(image, axis=0)

        low_threshold = 0.050
        high_threshold = 0.99
        prediction_prob = model.predict(image)[0][0]

        if prediction_prob < low_threshold or prediction_prob > high_threshold:
            prediction = "Normal"
        else:
            prediction = "Pneumonia"

        update_ai_suspected(patient['id'], prediction)
        update_clinician_to_review(id, 1)

    except Exception as e:
        print(f"Prediction error: {e}")

    session.pop('_flashes', None)

    if success:
        flash("Xray uploaded successfully.", "success")
    else:
        flash("Failed to upload xray.", "error")
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
    
    existing_image = get_xray_image(id)
    
    if existing_image:
        old_image_path = os.path.join(XRAY_FOLDER, existing_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
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
        session.pop('_flashes', None)
        flash("Email settings not configured, contact administrator.", "error")
        return redirect(url_for('patients.edit_patient', id=patient_id))

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
        session.pop('_flashes', None)
        flash("Failed to send email.", "error")
        return redirect(url_for('patients.edit_patient', id=patient_id))

    patient_name = f"{patient['first_name']} {patient['surname']}"
    worker_name = worker["name"]
    
    recipient_email = patient["email"] # this could be changed to an actual email address for real world testing
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
        
        session.pop('_flashes', None)
        flash("Email sent successfully.", "success")
    except smtplib.SMTPException as e:
        session.pop('_flashes', None)
        flash("Unexpected error sending email. Contact your administrator.", "error")
    except Exception as e:
        session.pop('_flashes', None)
        flash("Unexpected error sending email. Contact your administrator.", "error")
    finally:
        return redirect(url_for('patients.edit_patient', id=patient_id))

