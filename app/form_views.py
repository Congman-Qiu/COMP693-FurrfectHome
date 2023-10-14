from app import app
from flask import render_template, request, redirect, url_for, session, flash
from app.util import common, mail
from app.services import accounts, supervisors, convenors, students, scholarships, employment, forms, chair, administrator, email_service, departments
from app.models.form_model import Form, SectionA, SectionD, SectionE, SupervisorAnswer
from app.models.enums import Error, Section
from app.models.student_model import Student
from app.models.answer_model import Answer
from app.models.common_model import Season
from app.models.email_model import Email
from datetime import datetime, timedelta


# Form dashboard
@app.route("/form/")
def form():
    return render_template("form/form.html")


# Section A
@app.route("/form/section_a", methods=['GET', 'POST'])
def section_a():
    if request.method == 'POST':
        # only student can create/ update section A
        # but supervisor, convenors, and admin can view section A

        user_type = session['user_type']
        form_id = request.form.get('form_id')

        student = Student()
        student.user_id = session["user_id"]
        student.address = request.form.get('address')
        student.phone = request.form.get('phone')
        student.thesis_title = request.form.get('thesis_title')

        form = Form()
        form.form_id = form_id
        form.current_user_id = session["user_id"]
        form.current_section = Section.SECTION_A.value
        form.form_status_id = 1
        form.status_updated_date = datetime.now()
        form.is_active = 1
        form.is_current = 1

        existing_form = forms.get_form_by_form_id(form_id)

        if existing_form is None:
            form.is_student_submitted = 0
            form.is_supervisor_approved = 0
            form.is_convenor_submitted = 0
            form.is_admin_completed = 0
            form.is_chair_completed = 0
        else:
            form.is_student_submitted = existing_form.is_student_submitted
            form.is_supervisor_approved = existing_form.is_supervisor_approved
            form.is_convenor_submitted = existing_form.is_convenor_submitted
            form.is_admin_completed =  existing_form.is_admin_completed
            form.is_chair_completed = existing_form.is_chair_completed

        forms.update_form(form)
        students.save_student(student)

        if user_type == 'student':
            student_id = session["user_id"]
            user_id = students.get_user_id(student_id)
        else:
            student_id = request.args.get('student_id')

        updated_form = forms.get_form_by_created_user_id(user_id)

        student = students.get_student_by_user_id(student_id)
        supervisors_list = supervisors.get_supervisors_by_student_id(student.student_id)
        scholarships_list = scholarships.get_scholarships_by_student_id(student.student_id)
        employment_list = employment.get_employment_by_student_id(student.student_id)

        flash("Section A is saved successfully.", category='success')
        return render_template("form/section_a.html",
                               form=updated_form,
                               form_id=form_id,
                               student=student,
                               student_id=student_id,
                               user_type=user_type,
                               supervisors=supervisors_list,
                               scholarships=scholarships_list,
                               employment=employment_list)
    elif request.method == 'GET':
        user_id = session["user_id"]
        user_type = session['user_type']
        form_id = request.args.get('form_id')

        if not user_type == 'student':
            student_id = request.args.get('student_id')
            user_id = students.get_user_id(student_id)
            
        if form_id is None:
            form = forms.get_form_by_created_user_id(user_id)
            form_id = form.form_id
        else:
            form = forms.get_form_by_form_id(form_id)

        student = students.get_student_by_user_id(user_id)
        supervisors_list = supervisors.get_supervisors_by_student_id(student.student_id)
        scholarships_list = scholarships.get_scholarships_by_student_id(student.student_id)
        employment_list = employment.get_employment_by_student_id(student.student_id)

        return render_template("form/section_a.html",
                               form=form,
                               form_id=form_id,
                               student=student,
                               student_id=student.student_id,
                               user_type=user_type,
                               supervisors=supervisors_list,
                               scholarships=scholarships_list,
                               employment=employment_list)


@app.route("/form/create_section_a")
def create_section_a():
    current_user_id = session["user_id"]
    user_type = session['user_type']

    form = Form()
    form.form_status_id = 1
    form.year = common.get_current_season().year
    form.month = common.get_current_season().month
    form.created_date = datetime.now().date()
    form.created_user_id = current_user_id
    form.current_user_id = current_user_id
    form.current_section = Section.SECTION_A.value
    form.status_updated_date = datetime.now().date()
    form.is_active = 1
    form.is_current = 1

    form_id = forms.create_form(form)

    student = students.get_student_by_user_id(current_user_id)
    supervisors_list = supervisors.get_supervisors_by_student_id(
        current_user_id)
    scholarships_list = scholarships.get_scholarships_by_student_id(
        current_user_id)
    employment_list = employment.get_employment_by_student_id(current_user_id)

    current_form = forms.get_form_by_form_id(form_id)

    flash("New 6MR form is created successfully.", category='success')

    return render_template("form/section_a.html",
                           form=current_form,
                           form_id=form_id,
                           student=student,
                           student_id=student.student_id,
                           supervisors=supervisors_list,
                           scholarships=scholarships_list,
                           employment=employment_list,
                           user_type=user_type)


# Section B
@app.route("/form/section_b/", methods=['GET', 'POST'])
def section_b():
    user_id = session["user_id"]
    user_type = session['user_type']

    if request.method == 'POST':
        form_id = request.form.get('form_id')
        answers_list = []

        for x in range(2, 10):  # loop through question 2 to 9
            answers_list.append((x, 1 if request.form.get(
                'nc_' + str(x)) == 'on' else 0, 0, 0))
        for x in range(10, 18):  # loop through question 10 to 17
            answers_list.append(
                (x, request.form.get('comp_date_' + str(x)), 0, 0))
        for x in range(18, 23):  # loop through question 18 to 22
            answers_list.append(
                (x, request.form.get('approval_' + str(x)), 0, 0))

        reporting_period = request.form.get('reporting_period')

        answers_list.append((23, reporting_period, 0, 0))

        save_answers(form_id, answers_list)

        questions_part_1 = forms.get_question_groups(2, 9)
        questions_part_2 = forms.get_question_groups(18, 22)
        answers_part_1 = forms.get_section_answers_for_question_range(
            form_id, Section.SECTION_B.value, 2, 17, user_id)
        answers_part_2 = forms.get_section_answers_for_question_range(
            form_id, Section.SECTION_B.value, 18, 22, user_id)
        answer_part_3 = forms.get_answer_by_question_id(form_id, 23)

        form = forms.get_form_by_form_id(form_id)

        flash("Section B saved successfully.", category='success')

        return render_template("form/section_b.html",
                               form=form,
                               form_id=form_id,
                               student_id=user_id,
                               user_type=user_type,
                               questions_part_1=questions_part_1,
                               questions_part_2=questions_part_2,
                               answers_part_1=answers_part_1,
                               answers_part_2=answers_part_2,
                               answer_part_3=answer_part_3,
                               reporting_periods_list=get_reporting_periods_list())
    elif request.method == 'GET':
        form_id = request.args.get('form_id')
        student_id = request.args.get('student_id')

        student_user_id = students.get_user_id(student_id)
        questions_part_1 = forms.get_question_groups(2, 9)
        questions_part_2 = forms.get_question_groups(18, 22)
        answers_part_1 = forms.get_section_answers_for_question_range(
            form_id, Section.SECTION_B.value, 2, 17, student_user_id)
        answers_part_2 = forms.get_section_answers_for_question_range(
            form_id, Section.SECTION_B.value, 18, 22, student_user_id)
        answer_part_3 = forms.get_answer_by_question_id(form_id, 23)

        form = forms.get_form_by_form_id(form_id)

        return render_template("form/section_b.html",
                               form=form,
                               form_id=form_id,
                               student_id=student_id,
                               user_type=user_type,
                               questions_part_1=questions_part_1,
                               questions_part_2=questions_part_2,
                               answers_part_1=answers_part_1,
                               answers_part_2=answers_part_2,
                               answer_part_3=answer_part_3,
                               reporting_periods_list=get_reporting_periods_list())


# Section C
@app.route("/form/section_c/", methods=['GET', 'POST'])
def section_c():
    if request.method == 'POST':
        form_id = request.form.get('form_id')
        user_id = session["user_id"]
        user_type = session["user_type"]
        student_id = request.form.get('student_id')

        answers_list = []

        for x in range(24, 44):  # loop through question 24 to 43
            answers_list.append((x, request.form.get('rate_' + str(x)), 0, 0))
        for x in range(44, 64):  # loop through question 44 to 63
            answers_list.append(
                (x, request.form.get('comment_' + str(x)), 0, 0))

        meeting_frequency = request.form.get('meeting_frequency')
        usual_feedback_period = request.form.get('usual_feedback_period')
        feedback_receiving_method = request.form.get(
            'feedback_receiving_method')

        answers_list.append((64, meeting_frequency, 0, 0))
        answers_list.append((65, usual_feedback_period, 0, 0))
        answers_list.append((66, feedback_receiving_method, 0, 0))

        save_answers(form_id, answers_list)

        questions_part_1 = forms.get_question_groups(24, 43)
        answers_part_1 = forms.get_section_answers_for_question_range(
            form_id, Section.SECTION_C.value, 24, 63, user_id)
        answer_part_2 = forms.get_answer_by_question_id(form_id, 64)
        answer_part_3 = forms.get_answer_by_question_id(form_id, 65)
        answer_part_4 = forms.get_answer_by_question_id(form_id, 66)

        form = forms.get_form_by_form_id(form_id)

        flash("Section C saved successfully.", category='success')

        return render_template("form/section_c.html",
                                form=form,
                                form_id=form_id,
                                student_id=user_id,
                                user_type=user_type,
                                questions_part_1=questions_part_1,
                                answers_part_1=answers_part_1,
                                answer_part_2=answer_part_2,
                                answer_part_3=answer_part_3,
                                answer_part_4=answer_part_4,
                                meeting_frequency_list=get_meeting_frequency_list(),
                                usual_feedback_period_list=get_usual_feedback_period_list(),
                                feedback_receiving_method_list=get_feedback_receiving_method_list())
    elif request.method == 'GET':
        form_id = request.args.get('form_id')
        user_id = session["user_id"]
        user_type = session["user_type"]
        student_id = request.args.get('student_id')

        student_user_id = students.get_user_id(student_id)
        questions_part_1 = forms.get_question_groups(24, 43)
        answers_part_1 = forms.get_section_answers_for_question_range(form_id, Section.SECTION_C.value, 24, 63, student_user_id)
        answer_part_2 = forms.get_answer_by_question_id(form_id, 64)
        answer_part_3 = forms.get_answer_by_question_id(form_id, 65)
        answer_part_4 = forms.get_answer_by_question_id(form_id, 66)

        form = forms.get_form_by_form_id(form_id)

        return render_template("form/section_c.html",
                               form=form,
                               form_id=form_id,
                               user_type=user_type,
                               student_id=student_id,
                               questions_part_1=questions_part_1,
                               answers_part_1=answers_part_1,
                               answer_part_2=answer_part_2,
                               answer_part_3=answer_part_3,
                               answer_part_4=answer_part_4,
                               meeting_frequency_list=get_meeting_frequency_list(),
                               usual_feedback_period_list=get_usual_feedback_period_list(),
                               feedback_receiving_method_list=get_feedback_receiving_method_list())


# Section D
@app.route("/form/section_d/", methods=['GET', 'POST'])
def section_d():

    user_type = session["user_type"]
    user_id = session['user_id']
    form_id = request.args.get('form_id')
    student_id = request.args.get('student_id')
    student_supervisor = None
    form = forms.get_form_by_created_user_id(student_id)

    if request.method == 'POST':
        form_id = request.form.get('form_id')
        student_id = request.form.get('student_id')

        save_section_d_answers(form_id, user_id, request)
        
        student_user_id = students.get_user_id(student_id)
        form_answers = get_section_d_answers(form_id, student_user_id)
        form = forms.get_form_by_form_id(form_id)

        flash("Section D saved successfully.", category='success')

        if (user_type == "supervisor"): 
            student_supervisor = supervisors.get_student_supervisor_by_user_id(user_id, student_id)

        return render_template("form/section_d.html",
                               form=form,
                               form_id=form_id,
                               form_answers=form_answers,
                               user_id=user_id,
                               student_id=student_id,
                               student_supervisor=student_supervisor,
                               user_type=user_type,)
    elif request.method == 'GET':
        student_user_id = students.get_user_id(student_id)
        form_answers = get_section_d_answers(form_id, student_user_id)
        form = forms.get_form_by_form_id(form_id)

        if (user_type == "supervisor"): 
            student_supervisor = supervisors.get_student_supervisor_by_user_id(user_id, student_id)

        return render_template("form/section_d.html",
                               form=form,
                               form_answers=form_answers,
                               form_id=form_id,
                               user_id=user_id,
                               student_id=student_id,
                               student_supervisor=student_supervisor,
                               user_type=user_type,)


# Section E
@app.route("/form/section_e/", methods=['GET', 'POST'])
def section_e():

    user_type = session["user_type"]
    user_id = session['user_id']
    supervisor = None
    convenor = None

    if request.method == 'POST':
        submit_user_type = request.form.get('submit_user_type')
        form_id = request.form.get('form_id')
        student_id = request.form.get('student_id')

        student_user_id = students.get_user_id(student_id)

        form = forms.get_form_by_form_id(form_id)
        student = students.get_student_by_user_id(student_user_id)

        if (user_type == "supervisor"):
            supervisor = supervisors.get_supervisor_by_user_id(user_id)

        if (user_type == "convenor"):
            convenor = convenors.get_convenor_by_user_id(user_id)

        save_section_e_answers(form_id, submit_user_type, request)

        answer_list = get_section_e_answers(form_id, student)

        flash("Section E saved successfully.", category='success')

        return render_template("form/section_e.html",
                               form=form,
                               form_id=form_id,
                               user_type=user_type,
                               student=student,
                               student_id=student_id,
                               supervisor=supervisor,
                               convenor=convenor,
                               answer_list=answer_list,
                               color_rating_list=get_color_rating_list(),
                               yes_no_na_list=get_yes_no_na_list(),)
    elif request.method == 'GET':
        form_id = request.args.get('form_id')
        student_id = request.args.get('student_id')

        student_user_id = students.get_user_id(student_id)

        form = forms.get_form_by_form_id(form_id)
        student = students.get_student_by_user_id(student_user_id)

        answer_list = get_section_e_answers(form_id, student)

        if (user_type == "supervisor"):
            supervisor = supervisors.get_supervisor_by_user_id(user_id)

        if (user_type == "convenor"):
            convenor = convenors.get_convenor_by_user_id(user_id)

        return render_template("form/section_e.html",
                               form=form,
                               form_id=form_id,
                               user_type=user_type,
                               student=student,
                               student_id=student_id,
                               supervisor=supervisor,
                               convenor=convenor,
                               answer_list=answer_list,
                               color_rating_list=get_color_rating_list(),
                               yes_no_na_list=get_yes_no_na_list(),)


# Section F
@app.route("/form/section_f/", methods=['GET', 'POST'])
def section_f():
    if request.method == 'POST':
        user_type = session["user_type"]
        form_id = request.form.get('form_id')

        # if chair provides feedback 
        if user_type == "chair":
            feedback = request.form.get("feedback")
            if feedback != "":
                # send feedback to student
                student_id = request.form.get('student_id')
                student_user_id = students.get_user_id(student_id)
                student = students.get_student_by_user_id(student_user_id)
                subject = "PG Tracker| You have received a feedback from Chair" 
                body = feedback
                
                email_service.email(student.email, subject, body)
            
            # set form is completed by chair
            forms.submit_form(form_id, user_type, 1)

            flash("Form is completed")
            return redirect(url_for('chair_dashboard'))
        
        # only student can create/ update section F
        student_id = request.form.get('student_id')

        # answers
        comments = request.form.get('comments')  # 86
        pg_chair = 1 if request.form.get('pg_chair') == 'on' else 0  # 87
        pg_convenor = 1 if request.form.get('pg_convenor') == 'on' else 0  # 88

        answers_list = []

        answers_list.append((86, comments, 0, 0))
        answers_list.append((87, pg_chair, 0, 0))
        answers_list.append((88, pg_convenor, 0, 0))

        save_answers(form_id, answers_list)
        
        form = forms.get_form_by_form_id(form_id)
        answers = forms.get_section_answers_by_form_id(
            form_id, Section.SECTION_F.value)

        flash("Section F is saved successfully.", category='success')

        return render_template("form/section_f.html",
                               form=form,
                               form_id=form_id,
                               answers=answers,
                               user_type=user_type,
                               student_id=student_id)
    elif request.method == 'GET':
        form_id = request.args.get('form_id')
        user_type = session["user_type"]
        student_id = request.args.get('student_id')

        form = forms.get_form_by_form_id(form_id)

        answers = forms.get_section_answers_by_form_id(
            form_id, Section.SECTION_F.value)

        return render_template("form/section_f.html",
                                form=form,
                                form_id=form_id,
                                answers=answers,
                                user_type=user_type,
                                student_id=student_id)


# Submit form
@app.route("/form/submit/", methods=['POST'])
def submit_form():
    form_id = request.form.get('form_id')
    user_type = session["user_type"]
    submit_type = request.form.get('submit_type')
    decline_reason = request.form.get('decline_reason')
    student_id = request.form.get('student_id')

    student_user_id = students.get_user_id(student_id)

    student = students.get_student_by_user_id(student_user_id)

    if (user_type == "supervisor"):
        if (submit_type == "approve"):
            forms.submit_form(form_id, user_type, 1)
            
            # save section e preset answers
            save_section_e_preset_answers(form_id, student_id)

            flash("6MR Form is submitted for other supervisors to review.",category='success')
        elif (submit_type == "decline"):
            forms.submit_form(form_id, user_type, 0)
            forms.submit_form(form_id, "student", 0)
            
            email_body_decline_message = """
            Hello """ + student.student_first_name + """,
            Your 6MR form is declined by your supervisor. The reason is: """ + decline_reason + """
            """

            email_service.email(student.email, "6MR Form is declined", email_body_decline_message)

            flash("6MR Form is declined and email has been sent to the student.",category='success')
        return redirect(url_for('supervisor_dashboard'))

    # submit the form
    forms.submit_form(form_id, user_type, 1)

    # send emails and return to dashboard
    if (user_type == "student"):
        student_supervisors = supervisors.get_supervisors_by_student_id(student_id)
        for supervisor in student_supervisors:
            if supervisor.supervisor_type == "principal":
                supervisor_email_body = "Your supervisee's 6MR form is submitted. Please complete your sections."
                email_service.email(supervisor.email, "6MR Form is submitted", supervisor_email_body)
        
        flash("6MR Form is submitted for principal supervisor to review.",category='success')
        return redirect(url_for('student_dashboard'))

    if (user_type == "convenor"):
        admin = administrator.get_admin_details()
        email_service.email(admin.email, "6MR Form is submitted", "6MR Form is submitted by convenor.")
        
        flash("6MR Form is submitted.", category='success')
        return redirect(url_for('convenor_dashboard'))

    if (user_type == "administrator"):
        section_f_answers = forms.get_section_answers_for_question_range(form_id, Section.SECTION_F.value, 86, 88, None)

        subject = "6MR Form Completed"

        email_to_student_body = "Your 6MR form is completed."
        email_to_supervisor_body = "Your supervisee's 6MR form is completed."
        
        student_user_id = students.get_user_id(student_id)
        student = students.get_student_by_user_id(student_user_id)
        email_service.email(student.email, subject, email_to_student_body)

        supervisor_ids = supervisors.get_supervisor_ids_by_form_id(form_id)
        for supervisor_id in supervisor_ids:
            supervisor_user_id = supervisors.get_supervisor_user_id(supervisor_id[0])
            supervisor = supervisors.get_supervisor_by_user_id(supervisor_user_id)
            email_service.email(supervisor.email, subject, email_to_supervisor_body)

        if section_f_answers:
            if len(section_f_answers[0]) > 0:
                email_body = "Student has filled Section F of the 6MR form. Please get in touch with relevant parties about the concerns raised."
                chair_details = chair.get_chair_details()
                email_service.email(chair_details.email, subject, email_body)

        flash("6MR Form is completed.", category='success')
        return redirect(url_for('administrator_dashboard'))


# 6MR Progress
@app.route("/form/forms/", methods=['GET'])
def progress():
    user_type = session["user_type"]

    current_forms = forms.get_all_forms(1)

    return render_template("form/forms.html", 
                            forms=current_forms)


# 6MR reminder emails for incompleted forms
@app.route("/form/reminder/", methods=['GET', 'POST'])
def reminder():
    user_type = session["user_type"]

    if request.method == 'POST':
        if user_type == "administrator":  
            form_id = request.form.get('form_id')
            reminder_type = request.form.get('reminder_type')
            
            email_recipient = ""
            email_subject = "6MR Form Reminder"
            email_body = ""

            selected_form = forms.get_form_by_form_id(form_id)

            if reminder_type == "student":
                email_recipient = get_recipient_emails_for_form(form_id, "student")
                email_body = "Please complete your 6MR form (ID: " + form_id + ")."
            elif reminder_type == "main_supervisor":
                email_recipient = get_recipient_emails_for_form(form_id, "supervisor", "main")
                email_body = "Please complete Section E of the 6MR form and make the approval decision for the form (ID: " + form_id + ")."
            elif reminder_type == "co_supervisors":
                email_recipient = get_recipient_emails_for_form(form_id, "supervisor", "co")
                email_body = "Please complete Section E of the 6MR form (ID: " + form_id + ")."
            elif reminder_type == "complete":
                email_recipient = get_recipient_emails_for_form(form_id, "all")
                email_body = "6MR Form (ID: " + form_id + ") for " + selected_form.student_first_name + " " + selected_form.student_last_name + " is completed."

                form = Form()
                form.form_id = form_id
                form.current_user_id = session["user_id"]
                form.current_section = Section.SECTION_E.value
                form.form_status_id = 1
                form.status_updated_date = datetime.now()
                form.is_active = 1
                form.is_current = 1
                form.is_student_submitted = 1
                form.is_supervisor_approved = 1
                form.is_convenor_submitted = 1
                form.is_admin_completed = 1
                form.is_chair_completed = 0

                forms.update_form(form)

            
            email_service.email(email_recipient, email_subject, email_body)

            current_forms = forms.get_all_forms(1)
            flash("Email(s) sent to the relevant person(s).", category='success')
            return render_template("form/forms.html",
                                forms=current_forms)

        else:
            return render_template("accounts/login.html", login_error=False)
        

# save answers
def save_answers(form_id, answers_list, user_id = None):
    if user_id is None:
        user_id = session["user_id"]

    answer_model_list = []

    for answer in answers_list:
        answer_model = Answer()
        answer_model.form_id = form_id
        answer_model.question_id = answer[0]
        answer_model.answer_value = answer[1]
        answer_model.answer_group = answer[2]
        answer_model.sequence = answer[3]
        answer_model.answered_by = user_id
        answer_model.answered_date = datetime.now()

        answer_model_list.append(answer_model)

    forms.save_answers(form_id, answer_model_list)


# get reporting period list
def get_reporting_periods_list():
    reporting_periods_list = []
    reporting_periods_list.append((1, "1st 6-Month"))
    reporting_periods_list.append((2, "2nd 6-Month"))
    reporting_periods_list.append((3, "3rd 6-Month"))
    reporting_periods_list.append((4, "4th 6-Month"))
    reporting_periods_list.append((5, "5th 6-Month"))
    reporting_periods_list.append((6, "6th 6-Month"))

    return reporting_periods_list


# get reporting period list
def get_meeting_frequency_list():
    meeting_frequency_list = []
    meeting_frequency_list.append((1, "Weekly"))
    meeting_frequency_list.append((2, "Fortnightly"))
    meeting_frequency_list.append((3, "Monthly"))
    meeting_frequency_list.append((4, "Every 3 Months"))
    meeting_frequency_list.append((5, "Half Yearly"))
    meeting_frequency_list.append((6, "Not at all"))

    return meeting_frequency_list


# get usual feedback period list
def get_usual_feedback_period_list():
    usual_feedback_period_list = []
    usual_feedback_period_list.append((1, "1 Week"))
    usual_feedback_period_list.append((2, "2 Weeks"))
    usual_feedback_period_list.append((3, "1 Month"))
    usual_feedback_period_list.append((4, "3 Months"))

    return usual_feedback_period_list


# get feedback receiving method
def get_feedback_receiving_method_list():
    feedback_receiving_method_list = []
    feedback_receiving_method_list.append((1, "Soft Copy"))
    feedback_receiving_method_list.append(
        (2, "Comments on submitted material"))
    feedback_receiving_method_list.append((3, "Verbally"))
    feedback_receiving_method_list.append((4, "On a separate letter"))

    return feedback_receiving_method_list


# get color rating list
def get_color_rating_list():
    color_rating_list = []
    color_rating_list.append((1, "green_radio", "color-label green"))
    color_rating_list.append((2, "orange_radio", "color-label orange"))
    color_rating_list.append((3, "red_radio", "color-label red"))

    return color_rating_list


# get yes/no/na list
def get_yes_no_na_list():
    yes_no_na_list = []
    yes_no_na_list.append((1, "Yes"))
    yes_no_na_list.append((2, "No"))
    yes_no_na_list.append((3, "N/A"))

    return yes_no_na_list


# get answers by group
def get_answers_by_group(answers, group_count):

    answers_object = []

    for item in answers:
        a = ()
        for x in range(group_count):
            if item.answer_group == x + 1:
                a = a + (item.answer_group,
                         item.answer_value, item.sequence)
                answers_object.append(a)

    return answers_object


# get recipient email(s) for reminders
def get_recipient_emails_for_form(form_id, user_type, supervisor_type = None):
    recipients = forms.get_form_reminder_email_recipients(form_id)
    reminder_recipients = []

    for recipient in recipients:
        if user_type == "student":
            reminder_recipients.append(recipient.student_email)
            break   
        elif user_type == "supervisor":
            if recipient.supervisor_type == "principal" and supervisor_type == "main":
                reminder_recipients.append(recipient.supervisor_email)
                break
            elif recipient.supervisor_type == "co" and supervisor_type == "co":
                reminder_recipients.append(recipient.supervisor_email)
        elif user_type == "convenor":
            reminder_recipients.append(recipient.convenor_email)
            break
        elif user_type == "all":
            reminder_recipients.append(recipient.student_email)
            reminder_recipients.append(recipient.supervisor_email)
            reminder_recipients.append(recipient.convenor_email)
            break
    
    return ','.join(reminder_recipients)


# get section D answers
def get_section_d_answers(form_id, user_id):
    form = forms.get_form_by_form_id(form_id)
    previous_form_id = forms.get_previous_form_id(user_id, form.year, form.month)
    res_obj = forms.get_answers_by_question_id(previous_form_id, 67, user_id)
    res_obj_current = forms.get_answers_by_question_id(form_id, 67, user_id)
    res_obj_next = forms.get_answers_by_question_id(form_id, 71, user_id)
    achievements = forms.get_answers_by_question_id(form_id, 70, user_id)
    expenditure = forms.get_answers_by_question_id(form_id, 72, user_id)

    form_answers = SectionD()

    form_answers.objective_changed = forms.get_answer_by_question_id(form_id, 68)
    form_answers.comments = forms.get_answer_by_question_id(form_id, 73)
    form_answers.date = forms.get_answer_by_question_id(form_id, 74)

    # achievement answers
    for achievement in achievements:
        form_answers.achievements_list.append(
            (achievement.answer_value, achievement.sequence,))

    # expenditure answers
    for item in expenditure:
        form_answers.expenditure_list.append((
            item.answer_value,
            item.answer_group,
            item.sequence
        ))

    # current research objective answers
    if len(res_obj_current) == 0:
            for prev_obj in res_obj:
                form_answers.res_obj_list.append(prev_obj)
    else:
        for obj in res_obj_current:
            for prev_obj in res_obj:
                if obj.answer_group == prev_obj.answer_group and prev_obj.sequence == obj.sequence == 1:
                    obj.answer_value = prev_obj.answer_value
            if len(res_obj) > 0:
                form_answers.res_obj_list.append(obj)

    # next research objective answers
    for obj in res_obj_next:
        form_answers.next_res_obj_list.append((
            obj.answer_value,
            obj.answer_group,
            obj.sequence
        ))

    return form_answers


# save section D answers
def save_section_d_answers(form_id, user_id, request):
    answers_list = []

    form = forms.get_form_by_form_id(form_id)

    # get previous form answers for research objectives
    previous_form_id = forms.get_previous_form_id(user_id, form.year, form.month)
    previous_res_obj = forms.get_answers_by_question_id(
        previous_form_id, 67, user_id)

    for item in previous_res_obj:
        prefix = ''
        if item.sequence == 2:
            prefix = 'status_'
        elif item.sequence == 3:
            prefix = 'comment_'

        value = request.form.get(
            prefix + str(item.answer_group) + '_' + str(item.sequence))
        answers_list.append((67, value, item.answer_group, item.sequence))

    # achievement answers
    achievement_count = int(request.form.get('achievement_count'))
    if achievement_count >= 0:
        for x in range(0, achievement_count + 1):
            achievement = request.form.get('achievement_' + str(x))
            if achievement:
                answers_list.append(
                    (70, request.form.get("achievement_" + str(x)), 0, x))
    else:
        answers_list.append((70, "", 0, 0))

    # next research objectives answers
    research_objective_count = int(request.form.get('next_research_obj_count'))
    if research_objective_count >= 0:
        group_number = 1
        for x in range(0, research_objective_count + 1):
            next_objective = request.form.get(
                'next_objective_' + str(x) + '_1')
            completion_date = request.form.get(
                'completion_date_' + str(x) + '_2')
            problem = request.form.get('problem_' + str(x) + '_3')
            if next_objective:
                answers_list.append((71, next_objective, group_number, 1))
                answers_list.append((71, completion_date, group_number, 2))
                answers_list.append((71, problem, group_number, 3))
                group_number += 1
    else:
        answers_list.append((71, "", 1, 0))
        answers_list.append((71, "", 1, 0))
        answers_list.append((71, "", 1, 0))

    # expenditure answers
    research_expenditure_count = int(
        request.form.get('research_expenditure_count'))
    if research_expenditure_count >= 0:
        group_number = 1
        for x in range(0, research_expenditure_count + 1):
            item = request.form.get('item_' + str(x) + '_1')
            amount = request.form.get('amount_' + str(x) + '_2')
            notes = request.form.get('notes_' + str(x) + '_3')
            if item:
                answers_list.append((72, item, group_number, 1))
                answers_list.append((72, amount, group_number, 2))
                answers_list.append((72, notes, group_number, 3))
                group_number += 1
    else:
        answers_list.append((72, "", 1, 0))
        answers_list.append((72, "", 1, 0))
        answers_list.append((72, "", 1, 0))

    # other single field answers
    comments = request.form.get('comments')
    date = request.form.get('date')
    form_id = request.form.get('form_id')
    objective_changed = request.form.get('objective_changed')

    answers_list.append((68, objective_changed, 0, 0))
    answers_list.append((73, comments, 0, 0))
    answers_list.append((74, date, 0, 0))

    save_answers(form_id, answers_list)


# get section E answers
def get_section_e_answers(form_id, student):

    answer_list = SectionE()

    # get list of supervisors who filled the form
    supervisor_ids = supervisors.get_supervisor_ids_by_form_id(form_id)        

    date_convenor = None
    highlights = None
    color_rating = None
    convenor = None

    department_id = departments.get_department_id_by_student_id(student.student_id)
    convenor = convenors.get_convenor_by_department_id(department_id)

    for id in supervisor_ids:
        supervisor_answers = SupervisorAnswer()
        supervisor_id = id[0]

        supervisor_user_id = supervisors.get_supervisor_user_id(supervisor_id)
        supervisor = supervisors.get_supervisor_by_user_id(supervisor_user_id)
        student_supervisor = supervisors.get_student_supervisor_by_user_id(supervisor_user_id, student.student_id)
        
        supervisor_answers.supervisor_name = supervisor.first_name + " " + supervisor.last_name
        supervisor_answers.supervisor_type = student_supervisor.supervisor_type
        supervisor_answers.supervisor_id = id

        questions_perf_rating = forms.get_question_groups(75, 79)
        answers_perf_rating = forms.get_section_answers_for_question_range(form_id, Section.SECTION_E.value, 75, 79, supervisor_user_id)
        answer_recommendation = forms.get_answer_by_question_id(form_id, 80, supervisor_user_id)
        comments_supervisor = forms.get_answer_by_question_id(form_id, 81, supervisor_user_id)
        date_supervisor = forms.get_answer_by_question_id(form_id, 82, supervisor_user_id)
        date_convenor = forms.get_answer_by_question_id(form_id, 83)
        highlights = forms.get_answer_by_question_id(form_id, 84)
        color_rating = forms.get_answer_by_question_id(form_id, 85)

        supervisor_answers.performance_questions = questions_perf_rating
        supervisor_answers.performance_answers = answers_perf_rating
        supervisor_answers.recommendation_answers = answer_recommendation
        supervisor_answers.supervisor_comment_answers = comments_supervisor
        supervisor_answers.supervisor_date_answers = date_supervisor

        answer_list.supervisor_answers_list.append(supervisor_answers)

    answer_list.convenor_date_answers = date_convenor
    answer_list.highlight_answers = highlights
    answer_list.color_rating_answers = color_rating
    answer_list.convenor = convenor

    return answer_list


# section # answer pre-set
def save_section_e_preset_answers(form_id, student_id):
    # add empty answers for supervisors and convenors
    
    user_ids = []

    # get supervisors and convenors ids for the given student
    supervisors_list = supervisors.get_supervisors_by_student_id(student_id)
    
    department_id = departments.get_department_id_by_student_id(student_id)
    convenor = convenors.get_convenor_by_department_id(department_id)

    for supervisor in supervisors_list:
        supervisor_user_id = supervisors.get_supervisor_user_id(supervisor.supervisor_id)
        user_ids.append(supervisor_user_id)
    
    convenor_user_id = convenors.get_convenor_user_id(convenor.convenor_id)
    user_ids.append(convenor_user_id)

    for user_id in user_ids:
        answers_list = []
        answers_list.append((81, '', 0, 0))
        save_answers(form_id, answers_list, user_id)


# save section E answers
def save_section_e_answers(form_id, submit_user_type, request):
    
        answers_list = []

        answer_recommendation = request.form.get('recommendation')  # 80
        comments = request.form.get('comments')  # 81
        date_supervisor = request.form.get('date_supervisor')  # 82
        date_convenor = request.form.get('date_convenor')  # 84
        highlights = request.form.get('highlights')  # 85
        color_rating = request.form.get('color_rating')  # 86

        if submit_user_type == 'supervisor':
            for x in range(75, 80):  # loop through question 75 to 79
                answers_list.append(
                    (x, request.form.get('perf_rating_' + str(x)), 0, 0))
            answers_list.append((80, answer_recommendation, 0, 0))
            answers_list.append((81, comments, 0, 0))
            answers_list.append((82, date_supervisor, 0, 0))
        elif submit_user_type == 'convenor':
            answers_list.append((83, date_convenor, 0, 0))
            answers_list.append((84, highlights, 0, 0))
            answers_list.append((85, color_rating, 0, 0))

        save_answers(form_id, answers_list)


#get current forms
@app.route("/form/current_forms/")
def get_current_forms():
    user_type = session["user_type"]
    department_id = request.args.get("department_id")
    if department_id is not None:
        student_list = students.get_students_by_department_id(
            department_id)
    else:
        student_list = students.get_all_students()
    return render_template("/form/view_current_forms.html", student_list=student_list, user_type=user_type)


        