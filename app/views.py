from app import app
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.services import accounts, email_service, students, supervisors
from app.models.enums import Error, Section
from app.models.user_model import User
from app.models.student_model import Student
from app.models.email_model import Email
import bcrypt


# extra protection for session
app.secret_key = 'randompassword'


# home page
@app.route("/")
def index():
    return render_template("index.html")


# login
@app.route("/accounts/login", methods=['GET', 'POST'])
def login():
    login_error = None

    # POST request - login form submit
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        account = accounts.get_user_account(email, password)

        logged_in_user = account[0]
        login_error = account[1]

        if (logged_in_user and login_error == None):

            # set sessions to use throughout the application
            session['user_id'] = logged_in_user[0]
            session['email'] = logged_in_user[1]
            session['user_type'] = logged_in_user[2]

            login_error = False
            return redirect(url_for('dashboard'))
        else:
            login_error = "Invalid username or password"

            return render_template("accounts/login.html", login_error=login_error)
    # GET request
    else:
        return render_template("accounts/login.html", login_error=False)


# dashboard
@app.route("/dashboard/")
def dashboard():
    # route to the dashboard based on the user type

    if 'user_type' in session:
        user_type = session['user_type']

        if user_type == 'administrator':
            return redirect(url_for('administrator_dashboard'))
        elif user_type == 'student':
            return redirect(url_for('student_dashboard'))
        elif user_type == 'supervisor':
            return redirect(url_for('supervisor_dashboard'))
        elif user_type == 'convenor':
            return redirect(url_for('convenor_dashboard'))
        elif user_type == 'chair':
            return redirect(url_for('chair_dashboard'))
    
    else:
        return redirect(url_for('login'))


# error page
@app.route("/error")
def error():
    error_code = int(request.args.get('error_code'))
    error_message = None

    if error_code == Error.NO_PERMISSION.value:
        error_message = 'You do not have permission to view this page.'
    elif error_code == Error.NOT_FOUND.value:
        error_message = '404 Not Found! The page you are looking for does not exist.'
    else:
        error_message = 'An unknown error has occurred.'

    return render_template("error.html", error_message=error_message)


# logout
@app.route("/accounts/logout")
def logout():
    # remove session data, this will log the user out
    session.pop('email', None)
    session.pop('user_type', None)
    session.pop('user_id', None)

    return render_template("accounts/login.html")


# student register to the system function
@app.route("/accounts/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("accounts/register.html")
    else:
        register_message = None

        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        student_first_name = request.form.get(
            "student_first_name").capitalize()
        student_last_name = request.form.get("student_last_name").capitalize()
        department = request.form.get("department")
        phoneNumber = request.form.get("phoneNumber")

        #check if email already exists in database
        existing_user = accounts.get_user_by_email(email)

        #if password is not matched, show error message
        if password1 != password2:
            register_message = "Two passwords do not match. Please try again."

        # if email already exists, show error message
        elif existing_user != None:
            register_message = "Email already exists. Please try again."

        #check password is greater than 6 characters
        elif len(password1) < 6:
            register_message = 'Password must be at least 6 characters long.'

        if register_message:
            return jsonify({"error": register_message})

        else:
            #hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password1.encode('utf-8'), salt)

            #create new user object
            user = User(0, email, 'student', hashed_password, department)

            new_user_id = accounts.save_user(user)

            #create new student object

            new_student = Student()
            new_student.user_id = new_user_id
            new_student.student_first_name = student_first_name
            new_student.student_last_name = student_last_name
            new_student.phone = phoneNumber

            new_student_id = students.save_student(new_student)

            if new_user_id > 0 and new_student_id > 0:
                register_message = "User registered successfully! Your registration will be approved by Administration."

                #after registration, the email will be sent to students and admin

                subject = 'PGTracker Registration Received'
                body = f"""
                        Dear {student_first_name},
                        Thank you for registering with PGTracker! Your account is currently being reviewed and will be approved shortly.\nIf you have any urgent inquiries or need assistance, please contact our support team at pgtrackerlincoln@gmail.com\n\nBest regards,\nThe PGTracker Team
                """

                email_object = Email()

                email_object.email_to = email
                email_object.email_subject = subject
                email_object.email_body = body

                email_service.send_email(email_object)

                return jsonify({"success": register_message})

            return render_template('accounts/login.html')


# configure test email for testing purpose
@app.route("/config/email", methods=["GET", "POST"])
def config_email():
    if request.method == "GET":
        return render_template("config/email.html")
    else:
        email = request.form.get("config_email")

        accounts.update_test_email(email)
        email_service.email(email, "PGTracker Test Email", "You have set up the test email with your email address for PG Tracker Demo!")

        return redirect(url_for('dashboard'))