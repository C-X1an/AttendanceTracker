from cs50 import SQL
import datetime
from flask import Flask, render_template, redirect, flash, url_for, send_file, request, session
from flask_session import Session
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.cell.cell import WriteOnlyCell
from openpyxl.styles import Border, Side
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=1)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


DEPTS = ["DHQ", "DCS", "DMSP", "DSP"]
STATUS = ["Present", "Off", "Leave", "RSO", "Medical Leave", "MA", "Course", "AO"]

db = SQL("sqlite:///database.db")
def check_attendance():
    for attendance in db.execute("SELECT * FROM attendance"):
        try:
            if datetime.datetime.fromisoformat(attendance["date"]).date() < datetime.datetime.today().date():
                db.execute("DELETE FROM attendance")
                for user in db.execute("SELECT * FROM users WHERE username != 'superadmin'"):
                    db.execute("INSERT INTO attendance VALUES (?, ?, ?, '-', '-', '-', '-')", user["username"], user["employee_type"], user["department"])
        except ValueError:
            pass

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    # check through users table, if username valid, verify password. else, flash invalid account
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        match_account = db.execute("SELECT * FROM users WHERE username = ?", username)
        if check_password_hash(match_account[0]["hashed_password"], password):
            session["username"] = username
            if username == "superadmin":
                session["role"] = "admin"
                return redirect("/superadmin")
            else:
                session["role"] = "user"
                return redirect("/user_dashboard")
        else:
            flash("Invalid username or password", "error")
            return redirect("/login")
    else:
        try:
            if session["username"] == "superadmin":
                return redirect("/superadmin")
            else:
                return redirect("/user_dashboard")
        except KeyError:
            return render_template("login.html")


@app.route("/user_dashboard")
@login_required
def user_dashboard():
    check_attendance()
    # when attendance submitted, fetch morning and afternoon status and remarks if any.
    todays_attendance = db.execute("SELECT * FROM attendance WHERE username=?", session["username"])[0]
    return render_template("attendance_submit.html", todays_attendance=todays_attendance, username=session["username"])


@app.route("/submit-attendance", methods=["POST"])
@login_required
def submit_attendance():
    # verify valid status for both AM and PM, update to daily db of attendance, input date in datetime format
    if request.form.get("morning_present"):
        am_status = "Present"
    else:
        am_status = request.form.get("morning_reason")
    if request.form.get("afternoon_present"):
        pm_status = "Present"
    else:
        pm_status = request.form.get("afternoon_reason")
    if request.form.get("remarks"):
        remarks = request.form.get("remarks")
    else:
        remarks = "-"
    db.execute("UPDATE attendance SET morning_status=?, afternoon_status=?, remarks=?, date=? WHERE username=?", am_status, pm_status, remarks, datetime.datetime.today().date(), session["username"])
    return redirect("/user_dashboard")


@app.route("/reset-password", methods=["GET", "POST"])
@login_required
def reset_password():
    # make sure new != old, hash new password and update to db. redirect back to. if superadmin, redirect back to manage_users, if user redireect back to reset_password
    if request.method == "POST":
        if session["username"] != "superadmin":
            username, old_password, new_password, new_password_confirm = session["username"], request.form.get("old_password"), request.form.get("new_password"), request.form.get("confirm_password")
            hashed_old_password = db.execute("SELECT hashed_password FROM users WHERE username=?", session["username"])
            if not check_password_hash(hashed_old_password[0]["hashed_password"], old_password):
                flash("Password was not updated successfully", "error")
                return redirect("/reset-password")
        if session["username"] == "superadmin":
            username, new_password, new_password_confirm = request.form.get("username"), request.form.get("new_password"), request.form.get("confirm_password")
            hashed_old_password = db.execute("SELECT hashed_password FROM users WHERE username=?", username)
        if not new_password == new_password_confirm:
            flash("Password was not updated successfully", "error")
            if session["username"] == "superadmin":
                return redirect("/superadmin")
            else:
                return redirect("/reset-password")
        db.execute("UPDATE users SET hashed_password=? WHERE username=?", generate_password_hash(new_password), username)
        flash("Password has been successfully reset", "success")
        if session["username"] == "superadmin":
            return redirect("/superadmin")
        else:
            return redirect("/reset-password")
    else:
        return render_template("password_reset.html")


@app.route("/superadmin")
@login_required
@admin_only
def superadmin():
    check_attendance()
    # pass in user data
    users = db.execute("SELECT * FROM users WHERE username != 'superadmin'")
    # if session["username"] == "superadmin":
    return render_template("manage_users.html", users=users)
    # else:
    #     return redirect("/user_dashboard")


@app.route("/add-user", methods=["POST"])
@login_required
@admin_only
def add_user():
    # collect data from modal, update to db
    username, password, department, employee_type = request.form.get("username"), request.form.get("password"), request.form.get("department"), request.form.get("employee_type")
    try:
        db.execute("INSERT INTO users VALUES (?, ?, ?, ?)", username, employee_type, department, generate_password_hash(password))
        db.execute("INSERT INTO attendance VALUES (?, ?, ?, '-', '-', '-', '-')", username, employee_type, department)
        flash("User has successfully been added", "success")
    except ValueError:
        flash("User could not be added", "error")
    return redirect("/superadmin")


@app.route("/edit-user", methods=["POST"])
@login_required
@admin_only
def edit_user():
    global DEPTS
       # collect data from modal, update to db
    username, department, employee_type = request.form.get("username"), request.form.get("departmenet"), request.form.get("employee_type")
    if department in DEPTS:
        db.execute("UPDATE users SET employee_type=?, department=? WHERE username=?", employee_type, department, username)
        flash("User has successfully been edited", "success")
    else:
        flash("User was not edited", "error")
    return redirect("/superadmin")


@app.route("/remove-user", methods=["POST"])
@login_required
@admin_only
def remove_user():
    # collect data from modal, update to db
    username = request.form.get("username")
    db.execute("DELETE FROM users WHERE username=?", username)
    db.execute("DELETE FROM attendance WHERE username=?", username)
    flash("User has been successfully been removed", "success")
    return redirect("/superadmin")


@app.route("/attendance_report")
@login_required
@admin_only
def attendance_report():
    # pass in attendance information. 4 sets of information required, presence by department, absence by REG, and by reason, overall attendance .when updated, edit db. create function for 'generate-report'
    total_strength = 0
    present_strength = 0
    dept_strength = {}
    regular_absentees = {}
    absentee_by_reason = {}
    for period in ["AM", "PM"]:
        dept_strength[period] = {}
        for dept in DEPTS:
            dept_total_strength = count_department_strength(dept, "Total", period)
            dept_current_strength = count_department_strength(dept, "Present", period)
            total_strength += dept_total_strength
            present_strength += dept_current_strength
            dept_strength[period][dept] = str(dept_current_strength) + " / " + str(dept_total_strength)
        regular_absentees[period] = regular_absence(period)
        dept_strength[period]["ALL"] = str(present_strength) + " / " + str(total_strength)
        absentee_by_reason[period] = absence_by_reason(period)
    overall_attendance = db.execute("SELECT * FROM attendance")
    return render_template("attendance_report.html", dept_strength=dept_strength, regular_absentees=regular_absentees, absentee_by_reason=absentee_by_reason, overall_attendance=overall_attendance)


def count_department_strength(department, type, period):
    if type == "Total":
        if department == "ALL":
            return db.execute("SELECT COUNT(*) FROM attendance")[0]["COUNT(*)"]
        else:
            return db.execute("SELECT COUNT(*) FROM attendance WHERE department=?", department)[0]["COUNT(*)"]
    if type == "Present":
        if period == "AM":
            return db.execute("SELECT COUNT(*) FROM attendance WHERE department=? AND morning_status=?", department, type)[0]["COUNT(*)"]
        elif period == "PM":
            return db.execute("SELECT COUNT(*) FROM attendance WHERE department=? AND afternoon_status=?", department, type)[0]["COUNT(*)"]


def regular_absence(period):
    if period == "AM":
        return db.execute("SELECT username, remarks FROM attendance WHERE employee_type='REG' AND morning_status!='Present'")
    else:
        return db.execute("SELECT username, remarks FROM attendance WHERE employee_type='REG' AND afternoon_status!='Present'")


def absence_by_reason(period):
    # use list of absence reasons
    reasons = STATUS[1:]
    reason_data = {}
    for reason in reasons:
        remarks_for_reason = []
        if period == "AM":
            absence_data = db.execute("SELECT * FROM attendance WHERE morning_status=?", reason)
        elif period == "PM":
            absence_data = db.execute("SELECT * FROM attendance WHERE afternoon_status=?", reason)
        number_absentees = len(absence_data)
        if reason == "AO" or reason == "Leave":
            for absence in absence_data:
                if absence["remarks"] != "-":
                    remarks_for_reason.append(absence["remarks"])
        if remarks_for_reason:
            remarks_for_reason = str(remarks_for_reason).replace("[", "").replace("]", "")
        else:
            remarks_for_reason = "-"
        reason_data[reason] = [number_absentees, remarks_for_reason]
    return reason_data


@app.route("/generate-report")
@login_required
@admin_only
def generate_report():
    # The webpage URL whose table we want to extract
    url = "https://www.w3schools.com/html/html_tables.asp"

    # Assign the table data to a Pandas dataframe
    tables = pd.read_html(url)

    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet()

    cell = WriteOnlyCell(ws)
    cell.style = 'Pandas'


    def format_first_row(row, cell):
        thick = Side(style="thick", color="000000")
        cell.border = Border(top=thick, bottom=thick, left=thick, right=thick)
        for c in row[1:]:
            cell.value = c
            yield cell

    rows = dataframe_to_rows(tables[0])
    first_row = format_first_row(next(rows), cell)
    ws.append(first_row)

    def format_other_rows(row, cell):
        double = Side(style="thin", color="000000")
        cell.border = Border(top=double, bottom=double, left=double, right=double)
        for c in row[1:]:
            cell.value = c
            yield cell

    for row in rows:
        if row[0]:
            other_row = format_other_rows(row, cell)
            ws.append(other_row)

    wb.save("data.xlsx")
    return send_file("data.xlsx", as_attachment=True)


@app.route("/edit-attendance", methods=["POST"])
@login_required
@admin_only
def edit_attendance():
    # collect data from modal, update to db
    username, morning_status, afternoon_status, remarks = request.form.get("username"), request.form.get("morning_check_in"), request.form.get("afternoon_check_in"), request.form.get("remarks")
    if morning_status in STATUS and afternoon_status in STATUS:
        db.execute("UPDATE attendance SET morning_status=?, afternoon_status=?, remarks=? WHERE username=?", morning_status, afternoon_status, remarks, username)
        flash("Attendance has been successfully updated", "success")
    else:
        flash("Attendance was not updated", "error")
    return redirect("/attendance_report")


@app.route("/logout")
@login_required
def logout():
    # login required
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
