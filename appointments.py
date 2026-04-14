#---------------------------------------------------------------------------------------
# Name:        appointments.py
# Purpose:
# Author:      Chelo
# Created:     12/03/2026
# Copyright:   (c) Chelo 2026
#---------------------------------------------------------------------------------------
#===========================================
# IMPORTS
#===========================================
from datetime import datetime, time, timedelta, date

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from db import get_db
from helpers import login_required, is_admin, pretty_date


#===========================================
# BLUEPRINT SETUP
#===========================================
appointments = Blueprint("appointments", __name__)


#===========================================
# APPOINTMENT CONFIGURATION
#===========================================
SLOT_MINUTES = 30
OPEN_TIME = time(9, 0)
CLOSE_TIME = time(18, 0)

BARBERS = [
    {
        "id": "carlos",
        "name": "Carlos",
        "role": "Fades + Beard Specialist",
        "avatar": "barbers/carlos_avatar.jpg",
        "photos": ["barbers/carlos.tevez.jpg"]
    },
    {
        "id": "darwin",
        "name": "Darwin",
        "role": "Scissor Cuts + Styling",
        "avatar": "barbers/darwin_avatar.jpg",
        "photos": ["barbers/darwin.nunez.jpg"]
    },
    {
        "id": "leonel",
        "name": "Leonel",
        "role": "Blowouts + Classic Cuts",
        "avatar": "barbers/leonel_avatar.jpg",
        "photos": ["barbers/leonel.alvarez.jpg"]
    }
]

SERVICE_PRICES= {
    "Haircut": 25,
    "Beard": 15,
    "Haircut + Beard": 35
}


#===========================================
# TIME SLOT GENERATION
#===========================================
def generate_slots(date_obj):
    start = datetime.combine(date_obj, OPEN_TIME)
    end = datetime.combine(date_obj, CLOSE_TIME)
    slots = []
    cur = start
    while cur < end:
        slots.append(cur)
        cur += timedelta(minutes = SLOT_MINUTES)
    return slots


#===========================================
# ROUTES
#===========================================
@appointments.route("/", methods = ["GET", "POST"])
@login_required
def home():
    if request.method == "POST":

        if not session.get("user_id"):
            flash("You must be logged in to book an appointment.", "error")
            return redirect(url_for("auth.login", next=request.path))

        client_name = request.form.get("client_name", "").strip()
        barber = request.form.get("barber", "").strip()
        service = request.form.get("service", "").strip()
        price = SERVICE_PRICES.get(service, 0)
        appt_date = request.form.get("appt_date", "").strip()
        appt_time = request.form.get("appt_time", "").strip()
        notes = request.form.get("notes", "").strip()

        # Basic validation /// Prevents empty submissions.
        if not client_name or not barber or not service or not appt_date or not appt_time:
            flash("Please fill out: name, service, date, and time.", "error")
            return redirect(url_for("appointments.home"))

        # Validate date format (YYYY-MM-DD) and time (HH:MM).
        # If not in correct format, throw an error message.
        try:
            datetime.strptime(appt_date, "%Y-%m-%d")
            datetime.strptime(appt_time, "%H:%M")
        except ValueError:
            flash("Invalid date/time format. Use the pickers.", "error")
            return redirect(url_for("appointments.home"))

        # validate no past dates are being booked
        selected_date = datetime.strptime(appt_date, "%Y-%m-%d").date()

        if selected_date < date.today():
            flash("You cannot book a past date.", "error")
            return redirect(url_for("appointments.home"))

        # validate no past times are being booked
        selected_time = datetime.strptime(appt_time, "%H:%M").time()
        now = datetime.now()

        if selected_date == now.date() and selected_time <= now.time():
            flash("You cannot book a past time for today.", "error")
            return redirect(url_for("appointments.home"))

        conn = get_db()

        # Prevents two people booking same barber at same time.
        existing = conn.execute("""
            SELECT 1 FROM appointments
            WHERE barber = ? AND appt_date = ? AND appt_time = ?
        """, (barber, appt_date, appt_time)).fetchone()

        if existing:
            flash("That time slot is already booked.", "error")
            conn.close()
            return redirect(url_for("appointments.home"))


        user_id = session["user_id"]

        # Saves to database.
        conn.execute("""
            INSERT INTO appointments (client_name, barber, service, price, appt_date, appt_time, notes, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (client_name, barber, service, price, appt_date, appt_time, notes, user_id))
        conn.commit()
        conn.close()

        # flash("Appointment created.", "success") = Shows confirmation message.
        flash("Appointment created.", "success")
        return redirect(url_for("appointments.appointments_page"))

    return render_template("index.html", active = request.path)


@appointments.route("/appointments")
@login_required
def appointments_page():
    conn = get_db()

    """
    ORDER BY barber ASC, appt_date ASC, appt_time ASC
    Sorts appointments:
    - By barber
    - Then by date
    - Then by time
    """
    if is_admin():
        rows = conn.execute("""
            SELECT * FROM appointments
            ORDER BY barber ASC, appt_date ASC, appt_time ASC
        """).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM appointments
            WHERE user_id = ?
            ORDER BY barber ASC, appt_date ASC, appt_time ASC
        """, (session["user_id"],)).fetchall()

    conn.close()


    grouped = {}

    for r in rows:
        d = dict(r)
        d["appt_date_pretty"] = pretty_date(d["appt_date"])
        grouped.setdefault(d["barber"], []).append(d)

    barber_lookup = {b["name"]: b for b in BARBERS}

    return render_template("appointments.html", grouped=grouped, barber_lookup=barber_lookup, active=request.path)

#===========================================
# DASHBOARD (ADMIN ANALYTICS)
#===========================================
@appointments.route("/dashboard")
@login_required
def dashboard():
    if not is_admin():
        flash("Access denied.", "error")
        return redirect(url_for("appointments.home"))

    conn= get_db()

    filter_by= request.args.get("range", "all")
    start_date= request.args.get("start_date", "").strip()
    end_date= request.args.get("end_date", "").strip()

    if start_date and end_date:
        where_clause= f"WHERE appt_date BETWEEN '{start_date}' AND '{end_date}'"
        filter_by= "custom"
    elif start_date:
        where_clause= f"WHERE appt_date >= '{start_date}'"
        filter_by= "custom"
    elif end_date:
        where_clause= f"WHERE appt_date <= '{end_date}'"
        filter_by= "custom"
    elif filter_by == "7":
        where_clause= "WHERE appt_date >= date('now', '-7 days')"
    elif filter_by == "30":
        where_clause= "WHERE appt_date >= date('now', '-30 days')"
    else:
        where_clause= ""


    if filter_by == "7":
        filter_label= "Last 7 Days"
    elif filter_by == "30":
        filter_label= "Last 30 Days"
    elif filter_by == "custom":
        if start_date and end_date:
            filter_by= f"{pretty_date(start_date)} -> {pretty_date(end_date)}"
        elif start_date:
            filter_label= f"From {pretty_date(start_date)}"
        elif end_date:
            filter_label= f"Up to {pretty_date(end_date)}"
        else:
            filter_label= "Custom Range"
    else:
        filter_label= "All Time"

    #============================
    # BASIC STATS
    #============================
    total_appts= conn.execute(f"""
        SELECT COUNT(*) FROM appointments
        {where_clause}
    """).fetchone()[0]

    today_appts= conn.execute("""
        SELECT COUNT(*) FROM appointments
        WHERE appt_date = date('now')
    """).fetchone()[0]

    #============================
    # BASIC STATS
    #============================
    total_revenue= conn.execute(f"""
        SELECT COALESCE (SUM(price), 0)
        FROM appointments
        {where_clause}
    """).fetchone()[0]

    #============================
    # MOST POPULAR BARBER
    #============================
    top_barber= conn.execute(f"""
        SELECT barber, COUNT(*) as total
        FROM appointments
        {where_clause}
        GROUP BY barber
        ORDER BY total DESC
        LIMIT 1
    """).fetchone()

    #============================
    # MOST POPULAR SERVICE
    #============================
    top_service= conn.execute(f"""
        SELECT service, COUNT(*) as total
        FROM appointments
        {where_clause}
        GROUP BY service
        ORDER BY total DESC
        LIMIT 1
    """).fetchone()

    #============================
    # BUSIEST DAY
    #============================
    busiest_day= conn.execute(f"""
        SELECT appt_date, COUNT(*) as total
        FROM appointments
        {where_clause}
        GROUP BY appt_date
        ORDER BY total DESC
        LIMIT 1
    """).fetchone()

    #============================
    # BUSIEST TIME
    #============================
    busiest_time= conn.execute(f"""
        SELECT appt_time, COUNT(*) as total
        FROM appointments
        {where_clause}
        GROUP BY appt_time
        ORDER BY total DESC
        LIMIT 1
    """).fetchone()

    #============================
    # RECENT APPOINTMENTS
    #============================
    recent= conn.execute(f"""
        SELECT *
        FROM appointments
        {where_clause}
        ORDER BY appt_date DESC, appt_time DESC
        LIMIT 5
    """).fetchall()

    #============================
    # APPOINTMENTS PER BARBER
    #============================
    barber_stats= conn.execute(f"""
        SELECT barber, COUNT(*) as total
        FROM appointments
        {where_clause}
        GROUP BY barber
        ORDER BY total DESC
    """).fetchall()

    #============================
    # APPOINTMENTS PER SERVICE
    #============================
    service_stats= conn.execute(f"""
        SELECT service, COUNT(*) as total
        FROM appointments
        {where_clause}
        GROUP BY service
        ORDER BY total DESC
    """).fetchall()

    max_barber_total= max([item["total"] for item in barber_stats], default=1)
    max_service_total= max([item["total"] for item in service_stats], default=1)

    #============================
    # REVENUE BY BARBER
    #============================
    barber_revenue= conn.execute(f"""
        SELECT barber, SUM(price) as total
        FROM appointments
        {where_clause}
        GROUP BY barber
        ORDER BY total DESC
    """).fetchall()

    #============================
    # REVENUE BY SERVICE
    #============================
    service_revenue= conn.execute(f"""
        SELECT service, SUM(price) as total
        FROM appointments
        {where_clause}
        GROUP BY service
        ORDER BY total DESC
    """).fetchall()

    max_service_revenue= max([item["total"] for item in service_revenue], default=1)

    conn.close()

    return render_template(
        "dashboard.html",
        total_appts=total_appts,
        today_appts=today_appts,
        top_barber=top_barber,
        top_service=top_service,
        busiest_day=busiest_day,
        busiest_time=busiest_time,
        recent=recent,
        barber_stats=barber_stats,
        service_stats=service_stats,
        filter_by=filter_by,
        start_date=start_date,
        end_date=end_date,
        max_barber_total=max_barber_total,
        max_service_total=max_service_total,
        barber_revenue=barber_revenue,
        service_revenue=service_revenue,
        max_service_revenue=max_service_revenue,
        total_revenue=total_revenue,
        filter_label=filter_label
    )


@appointments.route("/barbers")
def barbers():
    service = request.args.get("service")
    return render_template(
        "barbers.html",
        barbers=BARBERS,
        service=service,
        active=request.path
    )

@appointments.route("/edit/<int:appt_id>", methods = ["GET", "POST"])
@login_required
def edit_appointment(appt_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db()

    if request.method == "POST":
        client_name = request.form.get("client_name", "").strip()
        service = request.form.get("service", "").strip()
        appt_date = request.form.get("appt_date", "").strip()
        appt_time = request.form.get("appt_time", "").strip()
        notes = request.form.get("notes", "").strip()

        if not client_name or not service or not appt_date or not appt_time:
            flash("Please fill out: name, service, date, and time.", "error")
            conn.close()
            return redirect(url_for("appointments.edit_appointment", appt_id = appt_id))

        try:
            datetime.strptime(appt_date, "%Y-%m-%d")
            datetime.strptime(appt_time, "%H:%M")
        except ValueError:
            flash("Invalid date/time format. Use the pickers.", "error")
            conn.close()
            return redirect(url_for("appointments.edit_appointment", appt_id = appt_id))

        selected_date = datetime.strptime(appt_date, "%Y-%m-%d").date()

        if selected_date < date.today():
            flash("You cannot select a past date.", "error")
            conn.close()
            return redirect(url_for("appointments.edit_appointment", appt_id = appt_id))

        selected_time = datetime.strptime(appt_time, "%H:%M").time()
        now = datetime.now()

        if selected_date == now.date() and selected_time <= now.time():
            flash("You cannot select a past time for today.", "error")
            conn.close()
            return redirect(url_for("appointments.edit_appointment", appt_id = appt_id))

        conn.execute("""
            UPDATE appointments
            SET client_name = ?, service = ?, appt_date = ?, appt_time = ?, notes = ?
            WHERE id = ?
        """, (client_name, service, appt_date, appt_time, notes, appt_id))

        conn.commit()
        conn.close()

        flash("Appointment updated.", "success")
        return redirect(url_for("appointments.appointments_page"))

    appt = conn.execute("SELECT * FROM appointments WHERE id = ?", (appt_id,)).fetchone()
    conn.close()

    if appt is None:
        flash("Appointment not found.", "error")
        return redirect(url_for("appointments.appointments_page"))

    selected_date = request.args.get("date", appt["appt_date"])

    conn = get_db()

    rows = conn.execute("""
        SELECT appt_time
        FROM appointments
        WHERE barber = ? AND appt_date = ? AND id != ?
    """, (appt["barber"], selected_date, appt_id)).fetchall()

    booked_times = {row["appt_time"] for row in rows}

    all_slots = []
    hour = 9
    minute = 0

    while True:
        t = f"{hour:02d}:{minute:02d}"
        all_slots.append(t)

        minute += 30
        if minute == 60:
            minute = 0
            hour += 1

        if hour == 18 and minute == 0:
            break

    selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    now = datetime.now()

    if selected_date_obj == now.date():
        current_time = now.strftime("%H:%M")
        all_slots = [t for t in all_slots if t > current_time or t == appt["appt_time"]]

    available_slots = [t for t in all_slots if t not in booked_times]

    conn.close()

    return render_template("edit.html", appt = appt, active = request.path, today=date.today().isoformat(),
                           selected_date = selected_date, available_slots = available_slots)


@appointments.route("/delete/<int:appt_id>", methods = ["POST"])
@login_required
def delete_appointment(appt_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db()
    conn.execute("DELETE FROM appointments WHERE id = ?", (appt_id, ))
    conn.commit()
    conn.close()
    flash("Appointment deleted.", "success")
    return redirect(url_for("appointments.appointments_page"))


@appointments.route("/barbers/<barber_id>")
@login_required
def barber_profile(barber_id):
    service = request.args.get("service")
    barber = next((b for b in BARBERS if b["id"] == barber_id), None)
    if not barber:
        return "Barber not found", 404

    conn = get_db()

    if is_admin():
        appts = conn.execute("""
            SELECT * FROM appointments
            WHERE barber = ?
            ORDER BY appt_date ASC, appt_time ASC
        """, (barber["name"],)).fetchall()
    else:
        appts = conn.execute("""
            SELECT * FROM appointments
            WHERE barber = ? AND user_id = ?
            ORDER BY appt_date ASC, appt_time ASC
        """, (barber["name"], session["user_id"])).fetchall()

    conn.close()


    selected_date = request.args.get("date")
    if not selected_date:
        selected_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()

    rows = conn.execute("""
    SELECT appt_time
    FROM appointments
    WHERE barber = ?
        AND appt_date = ?
    """, (barber["name"], selected_date)).fetchall()

    booked_times = {r["appt_time"] for r in rows}

    # generate 30-minute slots from 09:00 to 17:30
    all_slots = []
    hour = 9
    minute = 0

    while True:
        t = f"{hour:02d}:{minute:02d}"
        all_slots.append(t)

        minute += 30
        if minute == 60:
            minute = 0
            hour += 1

        if hour == 18 and minute == 0:
            break

    # convert selected_date to real date object
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    now = datetime.now()

    # if selected date is today, remove past times
    if selected_date == now.date():
        current_time = now.strftime("%H:%M")
        all_slots = [t for t in all_slots if t > current_time]

    available_slots = [t for t in all_slots if t not in booked_times]

    conn.close()
    # --- end slot logic ---

    return render_template(
        "barber_profile.html",
        barber=barber,
        appts=appts,
        selected_date=selected_date,
        available_slots=available_slots,
        service=service,
        active=request.path,
        today=date.today().isoformat()
    )

