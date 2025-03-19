from flask import Blueprint, render_template, redirect, url_for, request
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
            update_user(
                username=current_user,
                new_username=new_username,
                name=name,
                password=hashed_password,
                email=email,
            )
        else:
            update_user(
                username=current_user, new_username=new_username, name=name, email=email
            )

        return redirect(url_for("profile.view_profile"))
