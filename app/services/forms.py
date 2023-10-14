from app.models.form_email_recipient_model import FormEmailRecipient
from app.util import database
from app.models.form_model import Form
from app.models.answer_model import Answer
from app.models.workflow_model import Workflow
from app.util import common


def getCursor():
    return database.getCursor()


# create new form
def create_form(form: Form):
    cur = getCursor()
    cur.execute("""
        INSERT INTO form (
            form_status_id,
            year, 
            month, 
            created_user_id, 
            created_date, 
            current_user_id,
            current_section,
            status_updated_date,
            is_active,
            is_current)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        form.form_status_id,
        form.year,
        form.month,
        form.created_user_id,
        form.created_date,
        form.current_user_id,
        form.current_section,
        form.status_updated_date,
        form.is_active,
        form.is_current))

    form_id = cur.lastrowid

    # create workflow
    workflow = Workflow()
    workflow.form_id = form_id
    workflow.section_id = int(form.current_section)
    workflow.state = "Processing"
    workflow.created_date = form.created_date
    workflow.created_by = form.created_user_id

    create_workflow(workflow)

    return form_id


# update form
def update_form(form: Form):
    cur = getCursor()
    cur.execute("""
        UPDATE form
        SET form_status_id = %s,
            current_user_id = %s,
            current_section = %s,
            status_updated_date = %s,
            is_active = %s,
            is_current = %s,
            is_student_submitted = %s,
            is_supervisor_approved = %s,
            is_convenor_submitted = %s,
            is_admin_completed = %s,
            is_chair_completed = %s
        WHERE form_id = %s;
    """, (
        form.form_status_id,
        form.current_user_id,
        form.current_section,
        form.status_updated_date,
        form.is_active,
        form.is_current,
        form.is_student_submitted,
        form.is_supervisor_approved,
        form.is_convenor_submitted,
        form.is_admin_completed,
        form.is_chair_completed,
        form.form_id))

    return cur.lastrowid


# submit form
def submit_form(form_id, user_type, value):
    update_query = ""

    if user_type == None:
        return None

    if user_type == "supervisor":
        update_query = "SET is_supervisor_approved = " + str(value)

    if user_type == "student":
        update_query = "SET is_student_submitted = " + str(value)

    if user_type == "supervisor":
        update_query = "SET is_supervisor_approved = " + str(value)

    if user_type == "convenor":
        update_query = "SET is_convenor_submitted = " + str(value)

    if user_type == "chair":
        update_query = "SET is_chair_completed = " + str(value)    

    if user_type == "administrator":
        update_query = "SET is_admin_completed = " + str(value)

    final_update_query = """
        UPDATE form """ + update_query + """
        WHERE form_id = """ + form_id + """
    """

    cur = getCursor()
    cur.execute(final_update_query)


# get form by user_id
def get_form_by_created_user_id(student_id):
    season_year = common.get_current_season().year
    season_month = common.get_current_season().month
    # form is always created by student
    # so we take student_id as argument
    cur = getCursor()
    cur.execute("""
        SELECT 
            form_id,
            form_status_id,
            year, 
            month, 
            created_user_id, 
            created_date, 
            current_user_id,
            current_section,
            status_updated_date,
            is_current,
            is_student_submitted,
            is_supervisor_approved,
            is_convenor_submitted,
            is_admin_completed,
            is_active,
            '' as student_first_name,
            '' as student_last_name,
            '' as is_section_f_filled
        FROM form
        WHERE created_user_id = %s
            AND year = %s
            AND month = %s
            AND is_current = 1
            AND is_active = 1
        LIMIT 1;
    """, (student_id, season_year, season_month))

    form = cur.fetchone()

    if form is None:
        return None
    else:
        return get_form(form)


# get form by form_id
def get_form_by_form_id(form_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            F.form_id,
            form_status_id,
            year, 
            month, 
            created_user_id, 
            created_date, 
            current_user_id,
            current_section,
            status_updated_date,
            is_current,
            is_student_submitted,
            is_supervisor_approved,
            is_convenor_submitted,
            is_admin_completed,
            F.is_active,
            S.student_first_name,
            S.student_last_name,
            CASE WHEN 
                (SELECT COUNT(*)
				FROM form F
				LEFT JOIN answer A ON A.form_id = F.form_id
				LEFT JOIN question Q ON Q.question_id = A.question_id 
				WHERE Q.section_id = 6 AND Q.question_id = 86) > 0
                THEN 1 ELSE 0 END AS is_section_f_filled
        FROM form F
        JOIN student S ON S.user_id = F.created_user_id  
        WHERE 
            F.is_active = 1 AND
			F.form_id = %s
    """, (form_id,))

    form = cur.fetchone()

    if form is None:
        return None
    else:
        return get_form(form)


# get all forms
def get_all_forms(is_current=1, student_id=None, students_ids: tuple = None):

    filter_query = "1 = 1"

    if student_id is not None:
        filter_query = "created_user_id = " + str(student_id)
    
    if students_ids is not None:
        filter_query = "created_user_id IN (" + ",".join(students_ids) + ")"

    cur = getCursor()
    cur.execute("""
        SELECT 
            F.form_id,
            form_status_id,
            year, 
            month, 
            S.student_id, 
            created_date, 
            current_user_id,
            current_section,
            status_updated_date,
            is_current,
            is_student_submitted,
            is_supervisor_approved,
            is_convenor_submitted,
            is_admin_completed,
            F.is_active,
            S.student_first_name,
            S.student_last_name,
            CASE WHEN 
                (SELECT COUNT(*)
				FROM form F
				LEFT JOIN answer A ON A.form_id = F.form_id
				LEFT JOIN question Q ON Q.question_id = A.question_id 
				WHERE Q.section_id = 6 AND Q.question_id = 86) > 0
                THEN 1 ELSE 0 END AS is_section_f_filled
        FROM form F
        JOIN student S ON S.user_id = F.created_user_id
        WHERE 
            F.is_active = 1 AND
			is_current = %s AND """ +
            filter_query + """
        ORDER BY F.form_id DESC;
    """, (is_current,))

    forms = cur.fetchall()
    
    if forms is None:
        return None
    else:
        return get_forms_list(forms)


# create workflow
def create_workflow(workflow: Workflow):
    cur = getCursor()
    cur.execute("""
        INSERT INTO workflow (
            form_id,
            section_id,
            state,
            created_by,
            created_date
            )
        VALUES (%s, %s, %s, %s, %s);
    """, (
        workflow.form_id,
        workflow.section_id,
        workflow.state,
        workflow.created_by,
        workflow.created_date,))


# get answers for section
def get_section_answers_by_form_id(form_id, section_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            Q.question_id, 
            A.answer_value,
            A.answer_group,
            A.sequence
        FROM answer A
        JOIN question Q ON Q.question_id = A.question_id
        WHERE 
            form_id = %s
            AND Q.section_id = %s;
    """, (form_id, section_id))

    answer = cur.fetchall()

    return get_answer_list(answer)


# get answers for section by question range
def get_section_answers_for_question_range(form_id, section_id, start, end, answered_by):

    cur = getCursor()
    cur.execute("""
        SELECT 
            Q.question_id, 
            A.answer_value,
            A.answer_group,
            A.sequence
        FROM answer A
        JOIN question Q ON Q.question_id = A.question_id
        WHERE 
            form_id = %s
            AND Q.section_id = %s
            AND A.question_id BETWEEN %s AND %s
            AND A.answered_by = %s;
    """, (form_id, section_id, start, end, answered_by,))

    answer = cur.fetchall()

    return get_answer_list(answer)


# get answer by specific question_id
def get_answer_by_question_id(form_id, question_id, answered_by=None):

    answered_by_query = "AND 1 = 1"

    if answered_by is not None:
        answered_by_query = "AND A.answered_by = " + str(answered_by)

    cur = getCursor()
    cur.execute("""
        SELECT 
            Q.question_id, 
            A.answer_value,
            A.answered_by
        FROM answer A
        JOIN question Q ON Q.question_id = A.question_id
        WHERE 
            form_id = %s
            AND Q.question_id = %s """ +
                answered_by_query + """;
    """, (form_id, question_id))

    answer = cur.fetchone()

    if answer is None:
        return None
    else:
        answer_model = Answer()
        answer_model.question_id = answer[0]
        answer_model.answer_value = answer[1]
        answer_model.answered_by = answer[2]
        return answer_model


# get multiple answers by specific question_id
def get_answers_by_question_id(form_id, question_id, answered_by=None):
    cur = getCursor()
    cur.execute("""
        SELECT 
            Q.question_id, 
            A.answer_value,
            A.answer_group,
            A.sequence
        FROM answer A
        JOIN question Q ON Q.question_id = A.question_id
        WHERE 
            form_id = %s
            AND Q.question_id = %s;
    """, (form_id, question_id))

    answer = cur.fetchall()

    if answer is None:
        return None
    else:
        return get_answer_list(answer)


# get answer group by sequence
def get_answer_group_by_sequence(form_id, question_id, sequence, answered_by=None):
    cur = getCursor()
    cur.execute("""
        SELECT 
            Q.question_id, 
            A.answer_value,
            A.answer_group, 
            A.sequence
        FROM answer A
        JOIN question Q ON Q.question_id = A.question_id
        WHERE 
            form_id = %s
            AND Q.question_id = %s
            AND A.sequence = %s;
    """, (form_id, question_id, sequence))

    answer = cur.fetchall()

    if answer is None:
        return None
    else:
        return get_answer_list(answer)


# get previous 6MR form id
def get_previous_form_id(student_id, year, month):

    previous_season_month = None
    previous_season_year = None

    month_num = 6 if month == "June" else 12

    if month == "June":
        previous_season_month = "December"
        previous_season_year = year if month_num >= 12 else year - 1
    elif month == "December":
        previous_season_month = "June"
        previous_season_year = year

    cur = getCursor()
    cur.execute("""
        SELECT
            form_id
        FROM form
        WHERE
            year = %s AND
            month = %s AND
            created_user_id = %s AND
            is_active = 1
        """, (previous_season_year, previous_season_month, student_id))

    form = cur.fetchone()

    if form is None:
        return None
    else:
        return form[0]


# save answer for section
def save_answers(form_id, answers_list: list):

    rows = []
    rows_to_delete = []

    for answer in answers_list:
        rows.append((
            form_id,
            answer.question_id,
            answer.answer_value,
            answer.answered_by,
            answer.answer_group,
            answer.sequence,
            answer.answered_date
        ))

        rows_to_delete.append((
            form_id,
            answer.question_id,
            answer.answered_by
        ))

    # delete existing answers
    cur = getCursor()

    cur.executemany("""
        DELETE FROM answer
        WHERE
        form_id = %s
        AND question_id = %s
        AND answered_by = %s;
        """, rows_to_delete)

    # add new answers
    cur.executemany("""
        INSERT INTO answer (
            form_id,
            question_id,
            answer_value,
            answered_by,
            answer_group,
            sequence,
            answered_date
            )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, rows)


# get question groups
def get_question_groups(start, end):
    cur = getCursor()
    cur.execute("""
        SELECT 
            question_id,
            field_label_name,
            field_label_value,
            field_type,
            is_active
        FROM question
        WHERE 
            question_id BETWEEN %s AND %s
            AND is_active = 1;
    """, (start, end))

    questions = cur.fetchall()

    if questions is None:
        return None
    else:
        return questions


# get answer list
def get_answer_list(answer):
    if answer is None:
        return None
    else:
        answer_list = []
        for row in answer:
            answer_model = Answer()
            answer_model.question_id = row[0]
            answer_model.answer_value = row[1]
            answer_model.answer_group = row[2]
            answer_model.sequence = row[3]
            answer_list.append(answer_model)
        return answer_list


# get form (model)
def get_form(form):
    form_model = Form()

    form_model.form_id = form[0]
    form_model.form_status_id = form[1]
    form_model.year = form[2]
    form_model.month = form[3]
    form_model.created_user_id = form[4]
    form_model.created_date = form[5]
    form_model.current_user_id = form[6]
    form_model.current_section = form[7]
    form_model.status_updated_date = form[8]
    form_model.is_current = form[9]
    form_model.is_student_submitted = form[10]
    form_model.is_supervisor_approved = form[11]
    form_model.is_convenor_submitted = form[12]
    form_model.is_admin_completed = form[13]
    form_model.is_active = form[14]
    form_model.student_first_name = form[15]
    form_model.student_last_name = form[16]
    form_model.is_section_f_filled = form[17]

    return form_model


# get forms list (model)
def get_forms_list(forms):
    
    forms_list = []

    for form in forms:
        form_model = get_form(form)
        forms_list.append(form_model)

    return forms_list


# get form reminder email recipients
def get_form_reminder_email_recipients(form_id = None):
    filter_query = "1 = 1"

    if form_id is not None:
        filter_query = "F.form_id = " + form_id

    cursor = getCursor()
    cursor.execute("""
        SELECT
            F.form_id,
            UST.email as student_email,
            USS.email as supervisor_email,
            USC.email as convenor_email,
            SS.supervisor_type
        FROM form F
            JOIN student S ON S.user_id = F.created_user_id
            JOIN user UST ON UST.user_id = S.user_id
            JOIN student_supervisor SS ON SS.student_id = S.student_id
            JOIN supervisor SV ON SV.supervisor_id = SS.supervisor_id
            JOIN user USS ON USS.user_id = SV.user_id
            JOIN convenor C ON C.department_id = UST.department_id
            JOIN user USC ON USC.user_id = C.user_id
        WHERE
            F.is_active = 1 AND """
            + filter_query + """;

    """)

    recipients = cursor.fetchall()

    if recipients is None:
        return None
    else:
        return get_recipients_list(recipients)
    

# get recipient (model)
def get_recipient(recipient):
    recipient_model = FormEmailRecipient()

    recipient_model.form_id = recipient[0]
    recipient_model.student_email = recipient[1]
    recipient_model.supervisor_email = recipient[2]
    recipient_model.convenor_email = recipient[3]
    recipient_model.supervisor_type = recipient[4]

    return recipient_model


# get recipients list (model)
def get_recipients_list(recipients):
        
        recipients_list = []
    
        for recipient in recipients:
            recipient_model = get_recipient(recipient)
            recipients_list.append(recipient_model)
    
        return recipients_list