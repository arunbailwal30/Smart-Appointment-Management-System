import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import sys
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class User:
    def __init__(self, username="", password="", name="", phon=""):
        self.username = username
        self.password = password
        self.name = name
        self.phon = phon

    def set_name(self, name):
        self.name = name

    def set_username(self, username):
        self.username = username

    def set_phon(self, phon):
        self.phon = phon

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def check_username(self, username):
        return self.username == username

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
            username=data.get("username", ""),
            password=data.get("password", ""),
            name=data.get("name", ""),
            phon=data.get("phon", "")
        )

    def show_details(self):
        print(f"Name of customer: {self.name}")
        print(f"Contact number of customer: {self.phon}")

class Employee(User):
    def __init__(self, username="", password="", name="", designation="", phon=""):
        super().__init__(username, password, name, phon)
        self.designation = designation

    def set_designation(self, designation):
        self.designation = designation

    def get_designation(self):
        return self.designation

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
            username=data.get("username", ""),
            password=data.get("password", ""),
            name=data.get("name", ""),
            designation=data.get("designation", ""),
            phon=data.get("phon", "")
        )

    def show_details(self):
        print(f"Name of employee: {self.name}")
        print(f"Contact number of employee: {self.phon}")
        print(f"Designation of employee: {self.designation}")

class Appointment:
    def __init__(self, date="", start_time=0, end_time=0,
                 customer_username="", employee_username="", appointment_id=None):
        self.date = date  # "YYYY-MM-DD" string
        self.start_time = start_time  # hour integer 0-23
        self.end_time = end_time      # hour integer 0-23
        self.customer_username = customer_username
        self.employee_username = employee_username
        self.appointment_id = appointment_id

    def set_date(self, date):
        self.date = date

    def set_customer_username(self, username):
        self.customer_username = username

    def set_employee_username(self, username):
        self.employee_username = username

    def set_appointment_id(self, appointment_id):
        self.appointment_id = appointment_id

    def set_start_time(self, start_time):
        self.start_time = start_time

    def set_end_time(self, end_time):
        self.end_time = end_time

    def get_appointment_id(self):
        return self.appointment_id

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_date(self):
        return self.date

    def get_customer_username(self):
        return self.customer_username

    def get_employee_username(self):
        return self.employee_username

    def to_dict(self):
        return {
            "customerUsername": self.customer_username,
            "employeeUsername": self.employee_username,
            "appointmentId": self.appointment_id,
            "date": self.date,
            "startTime": self.start_time,
            "endTime": self.end_time
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            date=data.get("date", ""),
            start_time=data.get("startTime", 0),
            end_time=data.get("endTime", 0),
            customer_username=data.get("customerUsername", ""),
            employee_username=data.get("employeeUsername", ""),
            appointment_id=data.get("appointmentId", None)
        )

    def display_info(self):
        print("<---------Appointment Details---------->")
        print(f"Appointment Id: {self.appointment_id}")
        print(f"Start time: {self.start_time}")
        print(f"End time: {self.end_time}")
        print(f"Employee Id: {self.employee_username}")
        print(f"Customer Id: {self.customer_username}")
        print("<-------------------------------------->")

    def get_start_datetime(self):
        try:
            dt = datetime.strptime(self.date, "%Y-%m-%d")
            return dt.replace(hour=self.start_time, minute=0, second=0, microsecond=0)
        except Exception:
            return None

    def get_end_datetime(self):
        try:
            dt = datetime.strptime(self.date, "%Y-%m-%d")
            return dt.replace(hour=self.end_time, minute=0, second=0, microsecond=0)
        except Exception:
            return None

class AppointmentManager:
    def __init__(self, db):
        self.appointments_collection = db["Appointments"]
        self.appointments = []
        self.load_appointments()

    def load_appointments(self):
        self.appointments.clear()
        cursor = self.appointments_collection.find({})
        for doc in cursor:
            appt = Appointment.from_dict(doc)
            self.appointments.append(appt)
        self.remove_expired_appointments()

    def save_appointment(self, appt):
        self.appointments_collection.insert_one(appt.to_dict())
        self.appointments.append(appt)

    def add_appointment(self, appt):
        self.appointments.append(appt)

    def cancel_appointment(self, appointment_id, username):
        to_delete = []
        for appt in self.appointments:
            if (appt.appointment_id == appointment_id and username = appt.get_customer_username()):
                to_delete.append(appt)

        if len(to_delete) == 0:
            print("No matching appointment found to cancel.")
            return

        for appt in to_delete:
            self.appointments.remove(appt)
            self.appointments_collection.delete_one({
                "customerUsername": customer_username,
                "employeeUsername": employee_username,
                "date": date,
                "startTime": start_time
            })
        print("Appointment canceled successfully.")

    def is_available(self, employee_username, date, start_time, end_time):
        for appt in self.appointments:
            if appt.employee_username == employee_username and appt.date == date:
                if not (end_time <= appt.start_time or start_time >= appt.end_time):
                    return False
        return True

    def suggest_earliest_time_slot(self, employee_username, date):
        booked_slots = [1,2,3,4,5,6,7,8,18,19,20,21,22,23,24]
        for appt in self.appointments:
            if appt.employee_username == employee_username and appt.date == date:
                booked_slots.append((appt.start_time, appt.end_time))
        booked_slots.sort()

        earliest_start = 9  # 9AM
        for start, end in booked_slots:
            if earliest_start < start:
                return earliest_start
            earliest_start = max(earliest_start, end)
        return earliest_start

    def list_appointments_for_user(self, username, is_employee):
        print(f"Appointments for {username}:")
        found = False
        for appt in self.appointments:
            if (is_employee and appt.employee_username == username) or (not is_employee and appt.customer_username == username):
                found = True
                print(f"Date: {appt.date}, Start: {appt.start_time}, End: {appt.end_time}")
        if not found:
            print("No appointments found.")

    def remove_expired_appointments(self):
        now = datetime.now()
        expired = [appt for appt in self.appointments if appt.get_end_datetime() and appt.get_end_datetime() <= now]
        for appt in expired:
            self.appointments.remove(appt)
            self.appointments_collection.delete_one({
                "appointmentId": appt.appointment_id
            })

    def notify_user_appointments(self, username, is_employee):
        now = datetime.now()
        print(f"\n*** Upcoming appointments within next 1 hour for {username} ***")
        found = False
        for appt in self.appointments:
            user_match = (appt.employee_username == username if is_employee else appt.customer_username == username)
            if user_match:
                start_dt = appt.get_start_datetime()
                if start_dt:
                    diff = (start_dt - now).total_seconds()
                    if 0 < diff <= 3600:
                        found = True
                        print(f"Date: {appt.date}, Start: {appt.start_time}, End: {appt.end_time}")
        if not found:
            print("No upcoming appointments within the next hour.")
        print("***********************************************\n")

class UserManager:
    def __init__(self, db):
        self.employees_collection = db["Employees"]
        self.customers_collection = db["Customers"]

        self.employees = {}
        self.customers = {}

        self.load_users()

    def load_users(self):
        self.employees.clear()
        self.customers.clear()

        for doc in self.employees_collection.find({}):
            e = Employee.from_dict(doc)
            self.employees[e.username] = e

        for doc in self.customers_collection.find({}):
            c = Customer.from_dict(doc)
            self.customers[c.username] = c

    def save_employee(self, e: Employee):
        self.employees_collection.insert_one(e.to_dict())
        self.employees[e.username] = e

    def save_customer(self, c: Customer):
        self.customers_collection.insert_one(c.to_dict())
        self.customers[c.username] = c

    def login(self, username, password):
        if username in self.employees and self.employees[username].check_password(password):
            return True, True
        if username in self.customers and self.customers[username].check_password(password):
            return True, False
        return False, False

    def show_user_details(self, username, is_employee):
        if is_employee:
            if username in self.employees:
                self.employees[username].show_details()
            else:
                print("Employee not found.")
        else:
            if username in self.customers:
                self.customers[username].show_details()
            else:
                print("Customer not found.")

    def register_user(self, employee):
        username = input("Enter username: ").strip()
        if username in self.employees or username in self.customers:
            print("Username already exists! Choose another.")
            return False
        password = input("Enter password: ").strip()

        if employee:
            name = input("Enter employee full name: ").strip()
            designation = input("Enter position: ").strip()
            phon = input("Enter phone number: ").strip()
            e = Employee(username, password, name, designation, phon)
            self.save_employee(e)
            print("Employee registered successfully.")
        else:
            name = input("Enter full name: ").strip()
            phon = input("Enter contact info: ").strip()
            c = Customer(username, password, name, phon)
            self.save_customer(c)
            print("Customer registered successfully.")
        return True
    
    def register_user_web(self,username,password,name,phon,designation, employee):
        if username in self.employees or username in self.customers:
            print("Username already exists! Choose another.")
            return False
        password = password.strip()
        name = name.strip()
        phon = phon.strip()
        if employee:
            designation = designation.strip()
            e = Employee(username, password, name, designation, phon)
            self.save_employee(e)
            print("Employee registered successfully.")
        else:
            c = Customer(username, password, name, phon)
            self.save_customer(c)
            print("Customer registered successfully.")
        return True

    def get_employee(self, username):
        return self.employees.get(username, None)

    def get_customer(self, username):
        return self.customers.get(username, None)


class Software:
    def __init__(self):
        try:
            client = MongoClient(os.environ.get("APP_URI"), server_api=ServerApi('1'))
            client.admin.command('ping')
            self.client = client
            self.db = self.client["AppointmentManagement"]
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            sys.exit(1)

        self.user_manager = UserManager(self.db)
        self.appointment_manager = AppointmentManager(self.db)
        self.load_max_appointment_id()
        self.appointment_id_counter = len(self.appointment_manager.appointments) + 1
        if self.appointment_id_counter == 0:
            self.appointment_id_counter = 1

    def load_max_appointment_id(self):
        # Find max appointment id in DB and set counter accordingly to avoid duplicates
        max_id = 0
        for appt in self.db["appointments"].find({}):
            try:
                appt_id = appt.get("appointmentId", 0)
                if appt_id > max_id:
                    max_id = appt_id
            except Exception:
                continue
        self.appointment_id_counter = max_id + 1

    def run(self):
        print("******** Welcome to Smart Appointment Management System *********")
        while True:
            print("\n1. Login\n2. Register\n3. Exit")
            choice = input("Choose option: ").strip()
            if choice == '1':
                self.login()
            elif choice == '2':
                self.register_user()
            elif choice == '3':
                print("Exiting system...")
                break
            else:
                print("Invalid option. Try again.")
    def login_web(self, username, password):
        success, is_employee = self.user_manager.login(username, password)
        if success:
            return True
    
    def login(self):
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        success, is_employee = self.user_manager.login(username, password)
        if success:
            print(f"********** Login successful! Welcome {username} ************")
            self.appointment_manager.remove_expired_appointments()
            self.appointment_manager.notify_user_appointments(username, is_employee)
            if is_employee:
                self.employee_menu(username)
            else:
                self.customer_menu(username)
        else:
            print("Invalid username or password.")

    def register_user_web(self, username,password,name,phon,emp,designation=""):
            return self.user_manager.register_user_web(username,password,name,phon,designation,emp)

    def register_user(self):
        print("Register as:\n1. Employee\n2. Customer")
        reg_choice = input("Choose option: ").strip()
        if reg_choice == '1':
            self.user_manager.register_user(True)
        elif reg_choice == '2':
            self.user_manager.register_user(False)
        else:
            print("Invalid option.")

    def employee_menu(self, username):
        while True:
            print("\nEmployee Menu:\n1. View My Appointments\n2. Show My Details\n3. Logout")
            choice = input("Choose option: ").strip()
            if choice == '1':
                self.appointment_manager.list_appointments_for_user(username, True)
            elif choice == '2':
                self.user_manager.show_user_details(username, True)
            elif choice == '3':
                print("Logging out...")
                return
            else:
                print("Invalid option! Try again.")

    def customer_menu(self, username):
        while True:
            print("\nCustomer Menu:\n1. Book Appointment\n2. Cancel Appointment\n3. View My Appointments\n4. Show My Details\n5. Logout")
            choice = input("Choose option: ").strip()
            if choice == '1':
                self.book_appointment(username)
            elif choice == '2':
                self.cancel_appointment(username)
            elif choice == '3':
                self.appointment_manager.list_appointments_for_user(username, False)
            elif choice == '4':
                self.user_manager.show_user_details(username, False)
            elif choice == '5':
                print("Logging out...")
                return
            else:
                print("Invalid option! Try again.")

    def book_appointment(self, customer_username):
        date = input("Enter appointment date (YYYY-MM-DD): ").strip()
        print("Available employees:")
        for username, emp in self.user_manager.employees.items():
            print(f"- {username} ({emp.name}, {emp.designation})")

        employee_username = input("Enter employee username to book with: ").strip()
        if employee_username not in self.user_manager.employees:
            print("Employee username not found.")
            return
        suggested_start_time = self.appointment_manager.suggest_earliest_time_slot(employee_username, date)
        print(f"Suggested start time: {suggested_start_time}")

        try:
            start_time = int(input("Enter appointment start time (hour, 24h format, e.g., 14): ").strip())
            end_time = int(input("Enter appointment end time (hour, 24h format, e.g., 15): ").strip())
        except ValueError:
            print("Invalid input for time.")
            return

        if end_time <= start_time:
            print("Invalid time range.")
            return

        if self.appointment_manager.is_available(employee_username, date, start_time, end_time):
            new_appointment = Appointment(date, start_time, end_time, customer_username, employee_username, self.appointment_id_counter)
            self.appointment_id_counter += 1
            self.appointment_manager.save_appointment(new_appointment)
            print("Appointment booked successfully!")
        else:
            print("The selected time slot is not available.")

    def cancel_appointment(self, username):
        appointment_id = input("Enter appointment ID to cancel: ").strip()
        self.appointment_manager.cancel_appointment(appointment_id ,username)

if __name__ == '__main__':
    try:
        software = Software()
        software.run()
    except Exception as e:
        print(f"Exception occurred: {e}")
        sys.exit(1)

