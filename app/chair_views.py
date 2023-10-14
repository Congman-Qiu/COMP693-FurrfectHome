from app import app
from flask import render_template, request, redirect, url_for, session
from app.services import students,chair,scholarships,employment, supervisors


# Dashboard
@app.route("/chair/dashboard/")
def chair_dashboard():
    if "user_id" in session:
        return render_template("/chair/dashboard.html")
    else:
        return redirect(url_for('login'))


@app.route("/chair/manage_student_form")
def chair_manage_students_form():
    if "user_id" in session:
        students_list = students.get_students_who_submitted_section_f()
        students_list_arr = []
        for student in students_list:
            if student[5] == "" and student[6] == "0" and student[7] == "0":
                pass 
            elif student[5] == None and student[6] == None and student[7] == None:
                pass
            else: 
                students_list_arr.append(student)
        return render_template("chair/manage_student_forms.html", students_list_arr=students_list_arr)
    else:
        return redirect(url_for('login'))