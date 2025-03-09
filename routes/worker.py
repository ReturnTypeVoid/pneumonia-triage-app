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


from flask import Blueprint, request, render_template
from routes.auth import check_jwt_tokens, check_is_worker
from db import list_patients

worker = Blueprint('worker', __name__)

@worker.route('/dashboard')
def dashboard():
    # Authentication checks
    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    user_data, response = check_is_worker(user_data)
    if not user_data:
        return response

    # Get filter, search, and pagination parameters from request
    filter_status = request.args.get('status', 'all')  # e.g., 'suspected', 'normal'
    search_query = request.args.get('search', '')  # Search by name or ID
    page = int(request.args.get('page', 1))  # Pagination, default page 1
    per_page = 10  # Show 10 patients per page

    # Fetch patients from the database
    patients = list_patients(filter_status=filter_status, search_query=search_query)

    # Implement pagination (manually slicing results)
    total_patients = len(patients)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_patients = patients[start:end]

    # Pass data to template
    return render_template(
        'worker/dashboard.html',
        patients=paginated_patients,
        current_page=page,
        total_pages=(total_patients // per_page) + 1,
        filter_status=filter_status,
        search_query=search_query
    )

