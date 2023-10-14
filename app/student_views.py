from app import app
from app.services import students, notification, scholarships, employment, forms, email_service, supervisors
from datetime import datetime
from app.models.student_model import Student
from app.models.employment_model import Employment
from app.models.scholarship_model import Scholarship
from app.models.email_model import Email
from flask import render_template, request, redirect, url_for, session, flash
import mysql.connector



# Dashboard
@app.route("/student/dashboard/")
def student_dashboard():
    if "user_id" in session:
        user_id = session["user_id"]
        student_id = user_id
        student_name = students.get_student_name(user_id)[0][0]
        form = forms.get_form_by_created_user_id(user_id)

        return render_template("/student/dashboard.html",
                               student_name=student_name,
                               form=form,
                               student_id=student_id)
    else:
        return redirect(url_for('login'))


# All students / or students by department id
@app.route("/student/students/", methods=["GET", "POST"])
def all_students():
    user_type = session["user_type"]
    if request.method == 'GET':
        department_id = request.args.get("department_id")
        if department_id is not None:
            students_list = students.get_students_by_department_id(
                department_id)
        else:
            students_list = students.get_all_students()
        return render_template("student/students.html", students=students_list, user_type=user_type)
    elif request.method == "POST":
        user_input = request.form.get("search_student")
        searched_student = students.get_all_students(user_input)
        return render_template("student/students.html", students=searched_student, user_type=user_type)


# Update profile
@app.route("/student/update", methods=["GET", "POST"])
def student_update():
    if "user_id" in session:
        user_id = session["user_id"]
        user_type = session["user_type"]

        if request.method == "GET":
            student_id = request.args.get("student_id")
            if student_id is not None:
                user_id = students.get_user_id(student_id)

            personal_details = students.get_student_by_user_id(user_id)
            employment_details = employment.get_employment_by_student_id(
                personal_details.student_id)
            scholarship_details = scholarships.get_scholarships_by_student_id(
                personal_details.student_id)

            employment_details_len = len(employment_details) if len(
                employment_details) > 0 else 1
            scholarship_details_len = len(scholarship_details) if len(
                scholarship_details) > 0 else 1
            
            # admin get supervisor list
            main_sup_list = supervisors.get_supervisors(student_id, "principal")
            main_sup = main_sup_list[0] if main_sup_list else None

            co_sup_list = supervisors.get_supervisors(student_id, "co") 
            co_sup = co_sup_list if co_sup_list else None
            sup_list = supervisors.get_supervisor_by_department(student_id)
    
            return render_template("/student/update_profile.html",
                                   personal_details=personal_details,
                                   employment_details=employment_details,
                                   scholarship_details=scholarship_details,
                                   scholarship_details_len=scholarship_details_len,
                                   employment_details_len=employment_details_len,
                                   user_type=user_type,
                                   main_sup = main_sup,
                                   co_sup = co_sup,
                                   sup_list = sup_list)

        elif request.method == "POST":
            student_id = request.form.get("student_id")
            if student_id is not None:
                user_id = students.get_user_id(student_id)  
            
            if user_type == "administrator":
                # assign supervisor parts
                #delete old student_supervisor first 
                supervisors.student_supervisor_delete(student_id)

                #insert new student_supervisor
                co_sup_array = []
                for i in range(1, 4):
                    co_sup = request.form.get(f"co-sup{i}")
                    if co_sup != "-1" and co_sup.isdigit():
                        co_sup_array.append(int(co_sup))     


                try:
                    # Assign co-supervisors
                    for i in range(len(co_sup_array)):
                        supervisors.assign_co_supervisor(student_id, co_sup_id=co_sup_array[i])

                    # Assign main supervisor
                    main_sup_id = request.form.get("main-sup")
                    supervisors.assign_main_supervisor(student_id, main_sup_id)
                                
                except mysql.connector.errors.IntegrityError as e:
                    if e.errno == 1062:
                        error_message = "Duplicate entry: This student is already assigned to this supervisor."
                        flash(error_message)
                        return redirect(url_for('student_update', student_id=student_id))

                    
            employment_details_len = request.form.get("employment_details_len")
            scholarship_details_len = request.form.get(
                "scholarship_details_len")

            personal_details = students.get_student_by_user_id(user_id)
            employment_details = employment.get_employment_by_student_id(
                personal_details.student_id)
            scholarship_details = scholarships.get_scholarships_by_student_id(
                personal_details.student_id)

            #employment part-------------------------------
            # delete old emplyment records first

            if len(employment_details) > 0:
                student_id = request.form.get("student_id")
                employment.delete_employment_by_student_id([student_id])

            #insert new employment records
            #get how many employment first
            employment_count = request.form.getlist("employmentCount")

            #if there's no old employment history
            if employment_count == [""]:
                for i in range(1, int(employment_details_len) + 1):
                    employment_model = Employment()
                    employment_model.student_id = request.form.get(
                        "student_id")
                    employment_model.employment_type = request.form.get(
                        "employment_type{}".format(i))
                    employment_model.supervisor_name = request.form.get(
                        "supervisor_name{}".format(i))
                    hours_per_week = request.form.get(
                        "hours_per_week{}".format(i))
                    employment_model.hours_per_week = hours_per_week if hours_per_week != "" else None

                    #don't insert new employment if all fields are empty
                    if employment_model.employment_type or employment_model.supervisor_name or employment_model.hours_per_week:
                        employment.insert_employment(employment_model)

            #if there is old employment history
            else:
                employment_count = [int(y) for y in employment_count if y]
                max_emp_count = max(employment_count)

                for i in range(1, max_emp_count+1):
                    employment_model = Employment()
                    employment_model.student_id = request.form.get("stu_id")
                    employment_model.employment_type = request.form.get(
                        "employment_type{}".format(i))
                    employment_model.supervisor_name = request.form.get(
                        "supervisor_name{}".format(i))
                    hours_per_week = request.form.get(
                        "hours_per_week{}".format(i))
                    employment_model.hours_per_week = hours_per_week if hours_per_week != "" else None

                    #don't insert new employment if all fields are empty
                    if employment_model.employment_type or employment_model.supervisor_name or employment_model.hours_per_week:
                        employment.insert_employment(employment_model)

            #scholarship part------------------------------
            # delete old scholarship records first

            if len(scholarship_details) > 0:
                student_id = request.form.get("student_id")
                scholarships.delete_scholarship_by_student_id([student_id])

            #insert new scholarship records
            #get how many sholarship first
            scholarship_count = request.form.getlist("scholarshipCount")

            #if there's no old scholarship history
            if scholarship_count == [""]:
                for i in range(1, int(scholarship_details_len)+1):
                    scholarship_model = Scholarship()
                    scholarship_model.student_id = request.form.get(
                        "student_id")
                    scholarship_model.scholarship_name = request.form.get(
                        "sch_name{}".format(i))
                    sch_value = request.form.get("sch_value{}".format(i))
                    scholarship_model.value = sch_value if sch_value != "" else None
                    sch_start_date = request.form.get(
                        "sch_start_date{}".format(i))
                    scholarship_model.tenure = sch_start_date if sch_start_date != "" else None
                    sch_end_date = request.form.get("sch_end_date{}".format(i))
                    scholarship_model.end_date = sch_end_date if sch_end_date != "" else None

                    if scholarship_model.scholarship_name or scholarship_model.value or scholarship_model.tenure or scholarship_model.end_date:
                        scholarships.insert_scholarship(scholarship_model)

            #if there are old scholarship history
            else:
                scholarship_count = [int(x) for x in scholarship_count if x]
                max_count = max(scholarship_count)

                for i in range(1, max_count+1):
                    scholarship_model = Scholarship()
                    scholarship_model.student_id = request.form.get("stu_id")
                    scholarship_model.scholarship_name = request.form.get(
                        "sch_name{}".format(i))
                    sch_value = request.form.get("sch_value{}".format(i))
                    scholarship_model.value = sch_value if sch_value != "" else None
                    sch_start_date = request.form.get(
                        "sch_start_date{}".format(i))
                    scholarship_model.tenure = sch_start_date if sch_start_date != "" else None
                    sch_end_date = request.form.get("sch_end_date{}".format(i))
                    scholarship_model.end_date = sch_end_date if sch_end_date != "" else None

                    #don't insert new scholarship if the field is empty
                    if scholarship_model.scholarship_name or scholarship_model.value or scholarship_model.tenure or scholarship_model.end_date:
                        scholarships.insert_scholarship(scholarship_model)

            #update other details
            student = Student()
            student.user_id = user_id
            student.student_id = request.form.get("student_id")
            student.student_first_name = request.form.get('first_name')
            student.student_last_name = request.form.get("last_name")
            student.address = request.form.get("address")
            student.phone = request.form.get("phone_number")
            student.enrolment_date = request.form.get("enrol_date")

            students.save_student(student)

            flash("Profile has been updated", category='success')

            if user_type == "student":
                return redirect(url_for('student_update'))
            else:
                return redirect(url_for('all_students'))

    else:
        return redirect(url_for('login'))


# Approve a Student
@app.route('/student/approve', methods=['GET', 'POST'])
def approve_student():
    user_type = session.get("user_type")
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        approve_reject = request.form.get('approve_reject')

        user_id = students.get_user_id(student_id)
        student = students.get_student_by_user_id(user_id)

        if approve_reject == "approve":
            message = "Your registration has been approved by administration."
            email_object = Email()

            email_object.email_to = student.email
            email_object.email_subject = 'Student Registration Approved'
            email_object.email_body = message
            email_service.send_email(email_object)
            students.approve_reject_student(student_id, 1)
        elif approve_reject == "reject":
            message = request.form.get('message')
            email_object = Email()

            email_object.email_to = student.email
            email_object.email_subject = 'Student Registration Declined'
            email_object.email_body = message
            email_service.send_email(email_object)
            students.approve_reject_student(student_id, 0)

        if user_type == "administrator":
            return redirect(url_for('administrator_dashboard'))


# View a Student
@app.route('/student/student', methods=['GET', 'POST'])
def view_student():
    if "user_id" in session:
        user_id = session["user_id"]
        user_type = session["user_type"]

        if request.method == "GET":
            student_id = request.args.get("student_id")

            if student_id is not None:
                user_id = students.get_user_id(student_id)

            personal_details = students.get_student_by_user_id(user_id)
            employment_details = employment.get_employment_by_student_id(
                personal_details.student_id)
            scholarship_details = scholarships.get_scholarships_by_student_id(
                personal_details.student_id)

            employment_details_len = len(employment_details) if len(
                employment_details) > 0 else 1
            scholarship_details_len = len(scholarship_details) if len(
                scholarship_details) > 0 else 1

            return render_template("/student/student.html",
                                   personal_details=personal_details,
                                   employment_details=employment_details,
                                   scholarship_details=scholarship_details,
                                   scholarship_details_len=scholarship_details_len,
                                   employment_details_len=employment_details_len,
                                   user_type=user_type,)

        elif request.method == "POST":
            print("test")

    else:
        return redirect(url_for('login'))


#view student profile
@app.route("/view_profile")
def view_student_profile():
    user_id=session["user_id"]
    personal_details = students.get_student_by_user_id(user_id)
    employment_details = employment.get_employment_by_student_id(
        personal_details.student_id)
    scholarship_details = scholarships.get_scholarships_by_student_id(
        personal_details.student_id)

    return render_template("/student/view_profile.html", personal_details=personal_details, employment_details=employment_details, scholarship_details=scholarship_details )    




    