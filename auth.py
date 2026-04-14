#---------------------------------------------------------------------------------------
# Name:        auth.py
# Purpose:
# Author:      Chelo
# Created:     12/03/2026
# Copyright:   (c) Chelo 2026
#---------------------------------------------------------------------------------------
#===========================================
# IMPORTS
#===========================================
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db


#===========================================
# BLUEPRINT SETUP
#===========================================
auth = Blueprint("auth", __name__)


#=================================
# AUTHENTICATION ROUTES
#=====================================
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["first_name"] = user["first_name"]
            flash("Login successful!", "success")
            return redirect(url_for("appointments.home"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")



@auth.route("/logout", methods=["POST"])
def logout():

    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))



@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        birth_date = request.form.get("birth_date")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        consent = request.form.get("consent")
        not_robot = request.form.get("not_robot")

        # Validation
        if not all([first_name, last_name, email, birth_date, username, password]):
            flash("All required fields must be filled.", "error")
            return render_template("signup.html")

        if not consent:
            flash("You must accept data processing.", "error")
            return render_template("signup.html")

        if not not_robot:
            flash("Please confirm you are not a robot.", "error")
            return render_template("signup.html")

        conn = get_db()

        existing_user = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("Username or email already exists.", "error")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)

        conn.execute("""
            INSERT INTO users
            (first_name, last_name, email, phone, birth_date, username, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, birth_date, username, password_hash))

        conn.commit()
        conn.close()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")
