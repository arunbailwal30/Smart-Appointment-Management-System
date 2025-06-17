import os
from flask import (
    Flask, render_template, request, flash,
    redirect, url_for, session
)
from functools import wraps
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# MongoDB connection (set MONGODB_URI env var or default localhost)
MONGODB_URI = os.environ.get("APP_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client["AppointmentManagement"]


# User classes
class User:
    def __init__(self, username="", password="", name="", phon=""):
        self.username = username
        self.password = password
        self.name = name
        self.phon = phon


class Customer(User):
    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "name": self.name,
            "phon": self.phon
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("username", ""),
            data.get("password", ""),
            data.get("name", ""),
            data.get("phon", "")
        )


class Employee(User):
    def __init__(self, username="", password="", name="", designation="", phon=""):
        super().__init__(username, password, name, phon)
        self.designation = designation

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "name": self.name,
            "designation": self.designation,
            "phon": self.phon
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("username", ""),
            data.get("password", ""),
            data.get("name", ""),
            data.get("designation", ""),
            data.get("phon", "")
        )


# Decorator to require login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please fill in both username and password.", "danger")
            return render_template("login.html")

        # Try to find dashboard in employees and customers
        user_emp = db["Employees"].find_one({"username": username})
        user_cust = db["Customers"].find_one({"username": username})

        dashboard = None
        is_employee = False
        if user_emp and user_emp.get("password") == password:
            dashboard = user_emp
            is_employee = True
        elif user_cust and user_cust.get("password") == password:
            dashboard = user_cust
            is_employee = False

        if dashboard:
            session["username"] = username
            session["is_employee"] = is_employee
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

    return render_template("login.html")


@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        name = request.form.get("name", "").strip()
        phon = request.form.get("phon", "").strip()
        role = request.form.get("role", "Customer")
        designation = request.form.get("designation", "").strip()

        if not username or not password or not password_confirm or not name or not phon:
            flash("Please fill all required fields.", "danger")
            return render_template("signin.html")

        if password != password_confirm:
            flash("Passwords do not match.", "danger")
            return render_template("signin.html")

        # Check if username exists
        if db["Employees"].find_one({"username": username}) or db["Customers"].find_one({"username": username}):
            flash("Username already exists.", "danger")
            return render_template("signin.html")

        if role == "Employee":
            if not designation:
                flash("Designation is required for employee role.", "danger")
                return render_template("signin.html")
            db["Employees"].insert_one({
                "username": username,
                "password": password,
                "name": name,
                "phon": phon,
                "designation": designation
            })
        else:
            db["Customers"].insert_one({
                "username": username,
                "password": password,
                "name": name,
                "phon": phon
            })

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signin.html")


@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get("username")
    is_employee = session.get("is_employee", False)
    return render_template("dashboard.html", username=username, is_employee=is_employee)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route('/book_appointment', methods=["GET", "POST"])
@login_required
def book_appointment():
    if session.get("is_employee", False):
        flash("Employees cannot book appointments.", "warning")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        date = request.form.get("date", "").strip()
        start_time = request.form.get("start_time", "").strip()
        end_time = request.form.get("end_time", "").strip()
        employee_username = request.form.get("employee_username", "").strip()

        # Validation
        if not date or not start_time or not end_time or not employee_username:
            flash("All fields are required.", "danger")
            return redirect(url_for("book_appointment"))

        try:
            start_time = int(start_time)
            end_time = int(end_time)
            if start_time < 0 or start_time > 23 or end_time < 0 or end_time > 23:
                flash("Start and end times must be between 0 and 23.", "danger")
                return redirect(url_for("book_appointment"))
            if end_time <= start_time:
                flash("End time must be greater than start time.", "danger")
                return redirect(url_for("book_appointment"))
            datetime.strptime(date, "%Y-%m-%d")  # validate date
        except Exception:
            flash("Invalid input for date or time.", "danger")
            return redirect(url_for("book_appointment"))

        # Check employee exists
        employee = db["Employees"].find_one({"username": employee_username})
        if not employee:
            flash("Selected employee does not exist.", "danger")
            return redirect(url_for("book_appointment"))

        # Check overlapping appointments
        overlap_query = {
            "employeeUsername": employee_username,
            "date": date,
            "$or": [
                {"startTime": {"$lt": end_time, "$gte": start_time}},
                {"endTime": {"$gt": start_time, "$lte": end_time}},
                {"startTime": {"$lte": start_time}, "endTime": {"$gte": end_time}}
            ]
        }
        overlapping = db["Appointments"].find_one(overlap_query)
        if overlapping:
            flash("The selected time slot is not available.", "danger")
            return redirect(url_for("book_appointment"))

        # Compute next appointmentId
        latest = db["Appointments"].find_one(sort=[("appointmentId", -1)])
        next_id = (latest["appointmentId"] + 1) if latest else 1

        appointment = {
            "customerUsername": session["username"],
            "employeeUsername": employee_username,
            "date": date,
            "startTime": start_time,
            "endTime": end_time,
            "appointmentId": next_id
        }
        db["Appointments"].insert_one(appointment)
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("dashboard"))

    employees = list(db["Employees"].find({}, {"_id": 0, "username": 1, "name": 1, "designation": 1}))
    return render_template("book_appointment.html", employees=employees)


@app.route('/view_appointments')
@login_required
def view_appointments():
    username = session.get("username")
    is_employee = session.get("is_employee", False)
    query = {"$or": [{"employeeUsername": username}, {"customerUsername": username}]}
    appointments = list(db["Appointments"].find(query).sort([("date", 1), ("startTime", 1)]))
    return render_template("view_appointments.html", appointments=appointments, username=username, is_employee=is_employee)


@app.route('/cancel_appointment', methods=["GET", "POST"])
@login_required
def cancel_appointment():
    if session.get("is_employee", False):
        flash("Employees cannot cancel appointments.", "warning")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        date = request.form.get("date", "").strip()
        employee_username = request.form.get("employee_username", "").strip()
        start_time = request.form.get("start_time", "").strip()

        if not date or not employee_username or not start_time:
            flash("All fields are required.", "danger")
            return redirect(url_for("cancel_appointment"))

        try:
            start_time = int(start_time)
            datetime.strptime(date, "%Y-%m-%d")  # validate date format
        except Exception:
            flash("Invalid date or start time.", "danger")
            return redirect(url_for("cancel_appointment"))

        result = db["Appointments"].delete_one({
            "customerUsername": session["username"],
            "employeeUsername": employee_username,
            "date": date,
            "startTime": start_time
        })

        if result.deleted_count == 1:
            flash("Appointment canceled successfully.", "success")
        else:
            flash("No matching appointment found.", "warning")
            return redirect(url_for("cancel_appointment"))
        return redirect(url_for("dashboard"))

    employees = list(db["Employees"].find({}, {"_id": 0, "username": 1, "name": 1}))
    return render_template("cancel_appointment.html", employees=employees)


if __name__ == '__main__':
    app.run(debug=True)
     