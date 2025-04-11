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
    """
    Check if a file has an allowed extension.

    Description:
        Verifies that the uploaded file has a valid extension based on the allowed list.

    Arguments:
        filename (str): The name of the uploaded file.

    Returns:
        bool: True if the file is allowed, False otherwise.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder):
    """
    Save an uploaded file with a unique name.

    Description:
        Generates a unique filename and saves the file to the given folder.

    Arguments:
        file (FileStorage): The uploaded file.
        folder (str): Destination folder path.

    Returns:
        Tuple: (filename, full path)

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    unique_filename = f"{uuid.uuid4().hex}.jpg"
    save_path = os.path.join(folder, unique_filename)
    file.save(save_path)
    return unique_filename, save_path

@utilities.route('/users/avatar/upload', methods=['POST'])
def upload_avatar():
    """
    Route to upload a new avatar for the logged-in user.

    Description:
        Saves a new avatar file and removes the old one if it exists. 
        Flashes a success or error message after processing.

    Arguments:
        None

    Returns:
        Response: Redirects to the profile view page.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    current_user = get_user_from_token()['username']

    if 'file' not in request.files:
        flash('An error occured. Please contact your administrator.', 'error')
        return redirect(url_for('profile.view_profile'))

    file = request.files['file']

    if not allowed_file(file.filename):
        ext = os.path.splitext(file.filename)[1]
        flash(f'Invalid file type {ext}. Only .jpg and .jpeg files are supported.', 'error')
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
    """
    Route to upload an x-ray image for a patient.

    Description:
        Saves the new image, deletes the old one if it exists, updates the database,
        and runs an AI model to classify the image. Flags the case for clinician review.

    Arguments:
        id (int): Patient ID.

    Returns:
        Response: Redirects back to the patient edit page.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    patient = get_patient(id)

    if 'file' not in request.files:
        flash('An error occured. Please contact your administrator.', 'error')
        return redirect(url_for('patients.edit_patient', id=patient['id']))

    file = request.files['file']

    if not allowed_file(file.filename):
        ext = os.path.splitext(file.filename)[1]
        flash(f'Invalid file type ({ext}). Only .jpg and .jpeg files are supported.', 'error')
        return redirect(url_for('patients.edit_patient', id=patient['id']))

    
    existing_image = get_xray_image(patient['id'])
    if existing_image:
        old_image_path = os.path.join(XRAY_FOLDER, existing_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
            delete_xray_image(id)

    
    filename, path = save_file(file, XRAY_FOLDER)
    success = update_xray_image(patient['id'], filename)

    
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
    """
    Route to delete a patient's x-ray image.

    Description:
        Deletes the file and removes the image reference in the database. 
        Only accessible by workers and clinicians.

    Arguments:
        id (int): Patient ID.

    Returns:
        Response: Redirects to the patient edit page.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """
   
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
    """
    Route to send an email notification to a patient.

    Description:
        Sends a simple email using configured SMTP settings to notify the patient
        that their x-ray results are available. Only workers can use it.

    Arguments:
        patient_id (int): ID of the patient receiving the email.

    Returns:
        Response: Redirects to the patient edit page with a flash message.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

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
    
    recipient_email = patient["email"] 
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
