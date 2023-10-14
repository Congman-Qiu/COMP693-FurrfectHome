from app import app
from flask import render_template, request, redirect, url_for, flash, session
from app.services import reports, convenors, students, forms, supervisors, departments, email_service


# 6MR form status report
@app.route("/report/form_summary", methods=["GET", "POST"])
def form_summary_report():
    user_type = session.get("user_type")
    user_id = session.get("user_id")
    department_id = None
    
    if user_type == 'convenor':
        convenor = convenors.get_convenor_by_user_id(user_id)
        department_id = convenor.department_id
    students_status_list = reports.get_form_summary_report(department_id)

    if request.method == "GET":
        return render_template("report/form_summary.html", user_type=user_type, students_status_list=students_status_list)
    else:
        action_type = request.form.get("action_type")
        student_id = request.form.get("student_id")
        student_user_id = students.get_user_id(student_id)
        department_id = departments.get_department_id_by_student_id(student_id)
        student = students.get_student_by_user_id(student_user_id)
        convenor = convenors.get_convenor_by_department_id(department_id)

        subject = "6MR Form Action Required."
        body = ""
        recipient = ""
        
        if action_type == "red":
            body = "Your 6MR form resulted with some concerns. Set up a meeting with the department convenor ASAP."
            recipient = student.email
        elif action_type == "two_oranges":
            body = "Your progress has been 'modest'. Set up a meeting with the department convenor."
            recipient = student.email
        elif action_type == "orange":
            body = student.student_first_name + ' ' + student.student_last_name + "'s 6MR form has resulted an orange rating. Set up a meeting with the student's supervisor."
            recipient = student.email

        email_service.email(recipient, subject, body)

        return render_template("report/form_summary.html", user_type=user_type, students_status_list=students_status_list)


# performance analysis report list
@app.route("/report/performance_analysis_list")
def performance_analysis_report_list():

    faculty_performance_report_list = reports.get_performance_analysis_report_list()
	
    return render_template("report/performance_analysis_reports.html", faculty_performance_report_list=faculty_performance_report_list)


# performance analysis report
@app.route("/report/performance_analysis")
def performance_analysis_report():
    year = request.args.get("year")
    month = request.args.get("month")
    faculty_performance_list = reports.get_performance_analysis_report(year, month)
    faculty_pa_percentage_list = reports.get_pa_report_percentage(year, month)
	
    return render_template("report/performance_analysis_report.html", faculty_performance_list=faculty_performance_list, faculty_pa_percentage_list=faculty_pa_percentage_list,
    year = year, month = month)


# view historical 6mr
@app.route("/report/historical_forms")
def historical_6mr():
    user_type = session.get("user_type")
    user_id = session.get("user_id")
    prev_forms = None
    
    if user_type == "student":
        student = students.get_student_by_user_id(user_id)
        if student is not None:
            prev_forms = forms.get_all_forms(0, student.user_id) # 0 is for historical forms

    elif user_type == "supervisor":
        supervisor = supervisors.get_supervisor_by_user_id(user_id)
        if supervisor is not None:
            students_list = students.get_students_by_supervisor_id(supervisor.supervisor_id, search_term=None)
            
            student_id_tuple = ()
            for student in students_list:
                student_id_tuple += tuple(str(student.user_id))

            if student_id_tuple:  # Check if the list is not empty
                prev_forms = forms.get_all_forms(0, None, student_id_tuple)  # Pass the first element of the list
    elif user_type == "convenor":
         convenor = convenors.get_convenor_by_user_id(user_id)
         if convenor is not None:
            students_list = students.get_students_by_department_id(convenor.department_id, search_term=None)
            
            student_id_tuple = ()
            for student in students_list:
                student_id_tuple += tuple(str(student.user_id))

            if student_id_tuple:  # Check if the list is not empty
                prev_forms = forms.get_all_forms(0, None, student_id_tuple)


    elif user_type == "administrator" or "chair":
        # Retrieve full table without filter
        prev_forms = forms.get_all_forms(0)
    
    return render_template("report/historical_forms.html", forms=prev_forms)
