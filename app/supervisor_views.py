from app import app
from app.services import students, supervisors, accounts, departments
from flask import render_template, request, redirect, url_for, session, flash
from app.models.enums import Error
from app.models.supervisor_model import Supervisor


# Dashboard
@app.route("/supervisor/dashboard/")
def supervisor_dashboard():
    if "user_id" in session:
        user_id = session["user_id"]
        department_id = departments.get_department_id_by_user_id(user_id)[0]
        supervisor = supervisors.get_supervisor_by_user_id(user_id)
        return render_template("/supervisor/dashboard.html", supervisor=supervisor, department_id = department_id)
    else:
        return redirect(url_for('login'))


# View profile
@app.route("/supervisor/view/")
def supervisor_view():
    user_id = session["user_id"]
    supervisor = supervisors.get_supervisor_by_user_id(user_id)
    students_supervised = students.get_students_by_supervisor_id(
        supervisor.supervisor_id, None)
    return render_template("/supervisor/view_profile.html",
                           supervisor=supervisor,
                           students=students_supervised
                           )


# Update profile
@app.route("/supervisor/update/", methods=["GET", "POST"])
def supervisor_update():
    user_id = session["user_id"]
    if request.method == "GET":
        supervisor = supervisors.get_supervisor_by_user_id(user_id)

        return render_template("/supervisor/update_profile.html", supervisor=supervisor)

    #save updated info
    elif request.method == "POST":
        supervisor_to_update = Supervisor()
        supervisor_to_update.first_name = request.form.get('first_name')
        supervisor_to_update.last_name = request.form.get("last_name")
        supervisor_to_update.phone = request.form.get("phone_number")
        supervisor_to_update.supervisor_id = request.form.get("supervisor_id")

        supervisors.update_supervisor(supervisor_to_update)

        flash("Your profile has been updated", category='success')

        return redirect(url_for('supervisor_update'))


# supervisors by student id or department id
@app.route("/supervisor/supervisors")
def supervisors_filter():
    student_id = request.args.get("student_id")
    department_id = request.args.get("department_id")
    user_type = session["user_type"]
    user_id = session["user_id"]

    if student_id is not None:
        supervisors_list = supervisors.get_supervisors_by_student_id(
            student_id)
    if department_id is not None:
        supervisors_list = supervisors.get_supervisors_by_department_id(
            department_id)

    return render_template("supervisor/supervisors.html",
                           supervisors_list=supervisors_list,
                           user_type=user_type,)


# all supervisors
@app.route("/supervisor/supervisors/all")
def supervisors_all():
    supervisors_list = supervisors.get_all_supervisors()

    return render_template("supervisor/supervisors_all.html", supervisors_list=supervisors_list)


# view supervisees
@app.route("/supervisor/supervisees", methods=["GET", "POST"])
def view_supervisees():
    user_id = session["user_id"]
    if request.method == 'GET':
        supervisor_id = supervisors.get_supervisor_id(user_id)
        supervisees = students.get_students_by_supervisor_id(
            supervisor_id, None)
        return render_template("supervisor/supervisees.html",
                               supervisees=supervisees)
    elif request.method == "POST":
        user_input_raw = request.form.get("search_student")
        if user_input_raw == "%":
            user_input_raw = "0"
        if user_input_raw == "":
            user_input_raw = "0"
        user_input = "%" + user_input_raw + "%"

        searched_supervisees = students.get_students_by_supervisor_id(
            user_id, user_input)
        return render_template("supervisor/supervisees.html", supervisees=searched_supervisees)
