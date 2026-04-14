#---------------------------------------------------------------------------------------
# Name:        helpers.py
# Purpose:
#
# Author:      Chelo
#
# Created:     12/03/2026
# Copyright:   (c) Chelo 2026
#---------------------------------------------------------------------------------------
#===========================================
# IMPORTS
#===========================================
from datetime import datetime
from functools import wraps

from flask import session, flash, redirect, url_for, request


#===========================================
# AUTHORIZATION HELPERS
#===========================================
def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to book an appointment.", "error")
            return redirect(url_for("auth.login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def is_admin():
    return session.get("username") == "admin"


#===========================================
# DATE FORMATTING
#===========================================
def pretty_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A, %B %d, %Y")
    except:
        return date_str

