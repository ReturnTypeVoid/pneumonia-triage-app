# from flask import Blueprint, request, render_template
# from routes.auth import check_jwt_tokens, check_is_worker, get_user_from_token 
# from db import list_patients, get_user  

# worker = Blueprint('worker', __name__)

# @worker.route('/dashboard')
# def dashboard():
#     user_data, response = check_jwt_tokens()
#     if not user_data:
#         return response

#     user_data, response = check_is_worker(user_data)
#     if not user_data:
#         return response
    
#     current_user = get_user_from_token()['username']

#     return render_template('worker/dashboard.html', current_user=get_user(current_user), patients=list_patients())



#########################################################



from flask import Blueprint, request, render_template
from routes.auth import check_jwt_tokens, check_is_worker, get_user_from_token
from db import list_patients, get_user, get_user_id  

worker = Blueprint('worker', __name__)

@worker.route('/dashboard')
def dashboard():
    # Validate JWT Token
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    # This will check if User is a Worker
    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response
    
    # Get the current user's username
    token = request.cookies.get('access_token')  # token is stored in cookies
    if not token:
        return "Unauthorized", 401  # No token found
    
    user_info = get_user_from_token()  # Pass the token correctly
    if not user_info or 'username' not in user_info:
        return "Invalid User", 403  # Handle missing username
    
    current_user = user_info['username']
    
    #Fetch user data from the database
    user = get_user(current_user)
    if not user:
        return "User not found", 404  # Handle user not found in DB
    
    #Fetch patient data from the database
    patients = list_patients()
    
    # Render the dashboard template
    return render_template('worker/list_patients.html', user = get_user(current_user), patients=list_patients())

@worker.route('/dashboard/patients')
def worker_patients():
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response

    current_user = get_user_from_token()['username']
    user = get_user(current_user)

    # Get search query from request
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))  # Current page (pagination)
    per_page = 15  # Number of patients per page
    
    #Call list_patients with search_query
    patients = list_patients(search_query)  

    # Pagination logic
    total_patients = len(patients)
    total_pages = (total_patients + per_page - 1) // per_page  # Ceiling division
    start = (page - 1) * per_page
    end = start + per_page
    paginated_patients = patients[start:end]   

    return render_template('worker/list_patients.html',  
        current_page=page, total_pages=total_pages, search_query=search_query, patients=paginated_patients, user = get_user(current_user))


