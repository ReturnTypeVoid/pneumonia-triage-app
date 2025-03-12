# from flask import Blueprint, request, render_template
# from routes.auth import check_jwt_tokens, check_is_worker
# from db import list_patients

# worker = Blueprint('worker', __name__)

# @worker.route('/dashboard')
# def dashboard():
#     user_data, response = check_jwt_tokens()
#     if not user_data:
#         return response

#     user_data, response = check_is_worker(user_data)
#     if not user_data:
#         return response

#     return render_template('worker/dashboard.html', patients=list_patients())

# from flask import Blueprint, request, render_template
# from routes.auth import check_jwt_tokens, check_is_worker  # Auth functions
# from db import list_patients  # Returns patients assigned to a worker


# worker = Blueprint('worker', __name__)

# # Define the route for the worker dashboard
# @worker.route('/dashboard', methods=['GET'])  # Only handle GET requests
# def dashboard():
#     """
#     Displays a list of patients assigned to the currently logged-in worker.
#     """

#     # Verify the JWT tokens (authenticating the user)
#     user_data, response = check_jwt_tokens()
#     if not user_data:
#         return response  # Redirect to login or error page if not authenticated

#     # Check if the logged-in user is a worker
#     user_data, response = check_is_worker(user_data)
#     if not user_data:
#         return response  # Redirect to unauthorized page if not a worker

#     # Get the worker's ID from the authenticated user data
#     worker_id = user_data['user_id']

#     # Get filter, search, and pagination parameters from the request
#     status_filter = request.args.get('status', '').strip()  # Filter by patient status (optional)
#     search_query = request.args.get('search_query', '').strip()  # Search query (optional)
#     page = int(request.args.get('page', 1))  # Current page (pagination)
#     per_page = 10  # Number of patients per page

#     # Retrieve the list of patients assigned to the worker from the database
#     patients = list_patients(worker_id)  # List of patient dictionaries

#     # Filter patients by search query
#     if search_query:
#         search_query_lower = search_query.lower()
#         patients = [
#             patient for patient in patients
#             if search_query_lower in (patient.get('first_name', '') + ' ' + patient.get('surname', '')).lower()
#             or search_query_lower in patient.get('first_name', '').lower()
#             or search_query_lower in patient.get('surname', '').lower()
#             or search_query_lower in patient.get('email', '').lower()
#             or search_query_lower in patient.get('phone', '').lower()
#         ]

#     # Filter patients by status
#     if status_filter:
#         patients = [
#             patient for patient in patients
#             if patient.get('status', '').lower() == status_filter.lower()
#         ]

#     # Pagination logic
#     total_patients = len(patients)
#     total_pages = (total_patients + per_page - 1) // per_page  # Ceiling division for pages
#     start = (page - 1) * per_page
#     end = start + per_page
#     paginated_patients = patients[start:end]

#     # Render the dashboard template with the patients list and filters
#     return render_template(
#         'worker/dashboard.html',
#         patients=paginated_patients,
#         current_page=page,
#         total_pages=total_pages,
#         search_query=search_query,
#         status_filter=status_filter
#     )


# from flask import Blueprint, render_template
# from routes.auth import check_jwt_tokens, check_is_worker
# from db import list_patients

# worker = Blueprint('worker', __name__)

# @worker.route('/dashboard')
# def dashboard():
#     # Authentication check - verifies user is logged in
#     user_data, response = check_jwt_tokens()
#     if not user_data:
#         return response  # Returns redirect if not authenticated

#     # Authorization check - ensures user is a worker
#     user_data, response = check_is_worker(user_data)
#     if not user_data:
#         return response  # Returns error if not a worker

#     # Get patients specific to this worker using their ID from JWT
#     worker_id = user_data['worker_id']  # Get from authenticated user data
#     patients = list_patients(user_data)  # Filter by worker's ID

#     # Render template with patient data and worker context
#     return render_template(
#         'worker/dashboard.html',
#         patients=patients,
#         current_worker=user_data  # Pass worker details to template
#     )

# @worker.route('/dashboard')
# def dashboard():
#     # Authentication
#     user_data, auth_response = check_jwt_tokens()
#     if not user_data:
#         return auth_response

#     # Worker authorization
#     is_worker, worker_response = check_is_worker(user_data)
#     if not is_worker:
#         return worker_response

#     # Fetch worker ID from database
#     worker_id = (user_data['user_id'])
#     if not worker_id:
#         return "Error: Worker profile not found", 404

#     # Get worker-specific patients
#     patients = list_patients(worker_id)
    
#     return render_template('worker/dashboard.html', 
#                          patients=patients,
#                          worker_id=worker_id)


from flask import Blueprint, render_template
from routes.auth import check_jwt_tokens, check_is_worker
from db import list_patients

worker = Blueprint('worker', __name__)

@worker.route('/dashboard')
def dashboard():
    # Authentication check
    user_data, auth_response = check_jwt_tokens()
    if not user_data:
        return auth_response

    # Worker authorization check
    is_worker, worker_response = check_is_worker(user_data)
    if not is_worker:
        return worker_response

    # Get current user's ID (assuming JWT contains user_id)
    user_id = user_data.get('user_id')
    
    # Get patients assigned to this worker
    patients = list_patients(user_id)

    return render_template('worker/dashboard.html', 
                         patients=patients,
                         current_user=user_data)