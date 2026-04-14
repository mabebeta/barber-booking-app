#---------------------------------------------------------------------------------------
# Name:        barber_app
# Purpose:     creating an app that lets clients make, change, see and cancel
#              appointments
# Author:      Chelo
# Created:     12/02/2026
# Copyright:   (c) Chelo 2026
#---------------------------------------------------------------------------------------
#===========================================
# IMPORTS
#===========================================
import os
import sqlite3

from db import DB_NAME

#==============================
# DATABASE FUNCTIONS
#================================
def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            service TEXT NOT NULL,
            appt_time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Table ready: appointments")


#===============================
# APPOINTMENT FUNCTIONS
#==============================
def add_appointment():
    client_name = input("Client name: ")
    service = input("Service: ")
    appt_time = input("Appointment time: ")

    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
        INSERT INTO appointments (client_name, service, appt_time)
        VALUES (?, ?, ?)
    """, (client_name, service, appt_time))

    conn.commit()
    conn.close()

    print("Appointment saved!")


def show_appointments():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
        SELECT id, client_name, service, appt_time
        FROM appointments
    """)
    rows=cursor.fetchall()

    conn.close()

    print("\n--- All Appointments ---")

    if not rows:
        print("No appointments found.")
        return

    for row in rows:
        appt_id, name, svc, time = row
        print(f"{appt_id}. {name} | {svc} | {time}")


#=================================
# MENU FUNCTION
#=================================
def run_menu():
    while True:
        os.system("cls") # clears screen on Windows

        print("\n=== Barber App Menu ===")
        print("1. Add Appointment")
        print("2. View Appointment")
        print("3. Exit")

        print("\nWelcome to Alfredo's Barber App")
        choice = input("Choose an option: ")

        if choice == "1":
            add_appointment()
            input("\nPress Enter to continue...")
        elif choice == "2":
            show_appointments()
            input("\nPress Enter to continue...")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")
            input("\nPress Enter to continue...")


#=================================
# START PROGRAM
#===========================
if __name__=="__main__":
    create_table()
    run_menu()

