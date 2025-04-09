import os, uuid
import smtplib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, request, redirect, url_for
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

    # Remove existing X-ray if present
    existing_image = get_xray_image(patient['id'])
    if existing_image:
        old_image_path = os.path.join(XRAY_FOLDER, existing_image)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
            delete_xray_image(id)

    # Save the new file
    filename, path = save_file(file, XRAY_FOLDER)
    update_xray_image(patient['id'], filename)

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
    # Authentication check
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response  

    # Authorization check
    if not (check_is_worker(user_data) or check_is_clinician(user_data)):
        return response  

    # Determine if this is an AJAX request or direct browser request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Get SMTP settings
    settings = get_settings()
    if not settings:
        if is_ajax:
            return {"error": "SMTP settings not found"}, 500
        else:
            flash("SMTP settings not found", "error")
            return redirect(url_for('patients.view_patient', patient_id=patient_id))

    # Get user data
    current_user = get_user_from_token()["username"]
    patient = get_patient(patient_id)
    worker = get_user(current_user)

    if not patient or not worker:
        if is_ajax:
            return {"error": "Patient or worker not found"}, 404
        else:
            flash("Patient or worker not found", "error")
            return redirect(url_for('patients.patients_list'))

    # Validate patient email
    recipient_email = patient.get('email')
    if not recipient_email or not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email):
        return redirect(url_for('/patients/patient_form.html', id=patient_id))

    # Get SMTP settings with proper error handling
    settings = dict(get_settings())  # Convert sqlite.Row to dictionary
    if not settings:
        return {"error": "SMTP settings not found"}, 500

    # Validate required settings
    required_keys = [
        "smtp_server", "smtp_port", "smtp_tls",
        "smtp_username", "smtp_password", "smtp_sender"
    ]
    
    missing = [k for k in required_keys if not settings.get(k)]
    if missing:
        return {"error": f"Missing SMTP settings: {', '.join(missing)}"}, 500

    # Prepare email content
    patient_name = f"{patient['first_name']} {patient['surname']}"
    worker_name = worker["name"]
    
    subject = "X-ray Test Results"
    body = f"""Hello {patient_name},

Your chest x-ray results are now available. Please visit your local clinic at your earliest convenience.

Best regards,
{worker_name}
"""

    # Send the email
    try:
        # Prepare SMTP settings
        try:
            smtp_settings = {
                "smtp_server": settings["smtp_server"],
                "smtp_port": int(settings["smtp_port"]),  # Ensure port is an integer
                "smtp_tls": settings["smtp_tls"] in (True, 'True', 'true', '1', 1),  # Handle different true values
                "smtp_username": settings["smtp_username"],
                "smtp_password": settings["smtp_password"],
                "smtp_sender": settings["smtp_sender"]
            }
        except (KeyError, ValueError) as e:
            if is_ajax:
                return {"error": f"Invalid SMTP settings: {str(e)}"}, 500
            else:
                flash(f"Invalid SMTP settings: {str(e)}", "error")
                return redirect(url_for('patients.view_patient', patient_id=patient_id))

        # Create email message
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import smtplib

        msg = MIMEMultipart()
        msg["From"] = smtp_settings["smtp_sender"]
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP server
        server = smtplib.SMTP(smtp_settings["smtp_server"], smtp_settings["smtp_port"])
        
        # Enable debug output for troubleshooting
        server.set_debuglevel(1)
        
        # Identify ourselves to the server
        server.ehlo()
        
        # Use TLS if enabled
        if smtp_settings["smtp_tls"]:
            server.starttls()
            server.ehlo()  # Re-identify after TLS connection

        # Login if credentials are provided
        if smtp_settings["smtp_username"] and smtp_settings["smtp_password"]:
            server.login(smtp_settings["smtp_username"], smtp_settings["smtp_password"])
        
        # Send the email
        server.sendmail(smtp_settings["smtp_sender"], recipient_email, msg.as_string())
        
        # Close the connection properly
        server.quit()
        
        return redirect(url_for('patients.get_worker_patients'))

    except Exception as e:
        return {"error": f"Email sending failed: {str(e)}"}, 500
    