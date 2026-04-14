#---------------------------------------------------------------------------------------
# Name:        app.py
# Purpose:     customer website that connects to pythons app already built and
#              SQL database
# Author:      Chelo
# Created:     12/02/2026
# Copyright:   (c) Chelo 2026
#---------------------------------------------------------------------------------------
#===========================================
# IMPORTS
#===========================================
from flask import Flask

from auth import auth
from appointments import appointments
from db import init_db


#===================================
# APPLICATION SETUP
#================================
# Creates the Flask app
app = Flask(__name__)

# secret_key → required for flash messages (security feature)
app.secret_key = "dev-secret-change-later"


#===================================
# BLUEPRINT REGISTRATION
#================================
app.register_blueprint(auth)
app.register_blueprint(appointments)


#=================================
# APPLICATION START SECTION
#=================================
if __name__ == "__main__":
    init_db()
    app.run(debug = True)

