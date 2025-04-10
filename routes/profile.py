from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from routes.auth import (
    check_jwt_tokens,
    get_user_from_token,
    check_is_worker,
    check_is_clinician,
)
from db import get_user, check_user_exists, update_user
import bcrypt

profile = Blueprint("profile", __name__)

@profile.route("/profile/view", methods=["GET"])
def view_profile():
    """
    Route to view the logged-in user's profile.

    Description:
        Checks that the user is logged in and is either a worker or clinician.
        Then loads and displays their profile information.

    Arguments:
        None

    Returns:
        Response: Renders the profile view page.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    if not (check_is_worker(user_data) or check_is_clinician(user_data)):
        return response

    if not user_data:
        return response

    logged_in_user = get_user(get_user_from_token()["username"])

    return render_template(
        "profile/form.html", current_user=logged_in_user, user=logged_in_user
    )

@profile.route("/profile/update", methods=["POST"])
def update_profile():
    """
    Route to update the logged-in user's profile.

    Description:
        Handles changes to the user's username, name, email, and optionally their password.
        Checks for username conflicts and flashes a message based on the result.

    Arguments:
        None

    Returns:
        Response: Redirects to the profile view after processing the form.

    Author:
        Reece Alqotaibi (ReturnTypeVoid)
    """

    user_data, response = check_jwt_tokens()
    if not user_data:
        return response

    if not (check_is_worker(user_data) or check_is_clinician(user_data)):
        return response

    current_user = get_user_from_token()["username"]

    if request.method == "POST":
        new_username = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")

        if new_username != current_user and check_user_exists(new_username):
            return redirect(
                url_for("profile.view_profile", error="Username already exists.")
            )

        hashed_password = (
            bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            if password
            else None
        )

        if password:
            success = update_user(
                username=current_user,
                new_username=new_username,
                name=name,
                password=hashed_password,
                email=email,
            )
        else:
            success = update_user(
                username=current_user, new_username=new_username, name=name, email=email
            )

            session.pop('_flashes', None)

            if success:
                flash("Profile updated successfully.", "success")
            else:
                flash("Failed to update profile.", "error")

        return redirect(url_for("profile.view_profile"))
