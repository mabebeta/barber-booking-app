#---------------------------------------------------------------------------------------
# Name:        db.py
# Purpose:     database setup
# Author:      Chelo
# Created:     12/03/2026
# Copyright:   (c) Chelo 2026
#---------------------------------------------------------------------------------------
#===========================================
# IMPORTS
#===========================================
import sqlite3

from werkzeug.security import generate_password_hash


#=================================
# DATABASE CONFIGURATION
#=================================
DB_NAME = "database.db"


#===========================================
# DATABASE CONNECTION
#===========================================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


#===========================================
# DATABASE INITIALIZATION
#===========================================
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            client_name TEXT NOT NULL,
            barber TEXT NOT NULL,
            service TEXT NOT NULL,
            appt_date TEXT NOT NULL,
            appt_time TEXT NOT NULL,
            notes TEXT,
            price REAL NOT NULL DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            birth_date TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if not existing:
        hashed_pw = generate_password_hash("admin123")
        conn.execute("""
            INSERT INTO users
            (first_name, last_name, email, username, password)
            VALUES (?, ?, ?, ?, ?)
        """, ("Admin", "User", "admin@email.com", "admin", hashed_pw))

    conn.commit()
    conn.close()