from flask import Flask, redirect, url_for
from routes.auth import auth
from routes.profile import profile
from routes.utilities import utilities
from routes.patients import patients
from routes.users import users
from routes.settings import settings
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ydtuyiwhefu938792jr10917418hkjwlasja83'


app.register_blueprint(auth)
app.register_blueprint(profile)
app.register_blueprint(utilities)
app.register_blueprint(patients)
app.register_blueprint(users)
app.register_blueprint(settings)
@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0') 
