from app.models.supervisor_model import Supervisor
from app.models.student_supervisor_model import StudentSupervisor
from app.util import database
from app.services import students, supervisors


def getCursor():
    return database.getCursor()


# get supervisor full name
def get_supervisor_name(user_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            concat(first_name, " ", last_name ) AS full_name
        FROM supervisor 
        JOIN user 
        USING (user_id)
        WHERE user_id = %s;
    """, (user_id,))
    supervisor_name = cur.fetchall()
    print(supervisor_name)
    return supervisor_name


# get supervisor id by user id
def get_supervisor_id(user_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            supervisor_id
        FROM supervisor 
        WHERE user_id = %s;
    """, (user_id,))
    supervisor_id = cur.fetchone()

    if supervisor_id is None:
        return None
    return supervisor_id[0]


# get supervisor user id by supervisor id
def get_supervisor_user_id(supervisor_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            user_id
        FROM supervisor 
        WHERE supervisor_id = %s;
    """, (supervisor_id,))
    user_id = cur.fetchone()

    if user_id is None:
        return None
    return user_id[0]

# get supervisor by user id
def get_supervisor_by_user_id(user_id):
    cur = getCursor()
    cur.execute("""
        SELECT
            U.user_id,
            S.supervisor_id,
            '' AS supervisor_type,
            S.first_name,
            S.last_name,
            S.phone,
            U.email,
            D.department_name,
            '' AS supervisee_id
        FROM supervisor S
        JOIN user U ON U.user_id = S.user_id
        JOIN department D ON D.department_id = U.department_id
        WHERE S.user_id = %s;
    """, (user_id,))

    supervisor = cur.fetchone()

    if (supervisor is None):
        return None
    else:
        return get_supervisor(supervisor)


# get supervisors by student id
def get_supervisors_by_student_id(student_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            ST.user_id, 
            SS.supervisor_id,
            SS.supervisor_type, 
            S.first_name,
            S.last_name,
            S.phone,
            SP.email AS supervisor_email,
            D.department_name
        FROM 
            student ST
            JOIN student_supervisor SS ON ST.student_id = SS.student_id
            JOIN supervisor S ON SS.supervisor_id = S.supervisor_id
            JOIN user U ON ST.user_id = U.user_id
            JOIN department D ON U.department_id = D.department_id
            JOIN user SP ON SP.user_id = S.user_id
        WHERE 
            ST.student_id = %s
            AND U.is_active = 1;
    """, (student_id,))

    supervisors = cur.fetchall()

    if (supervisors is None):
        return None
    else:
        return get_supervisor_list(supervisors)


# get supervisors by department id
def get_supervisors_by_department_id(department_id):
    cur = getCursor()
    cur.execute("""
        SELECT
            U.user_id, 
            S.supervisor_id,
            '' AS supervisor_type,
            S.first_name, 
            S.last_name, 
            S.phone,
            U.email,
            D.department_name
        FROM 
            supervisor S
            JOIN user U ON S.user_id = U.user_id
            JOIN department D ON U.department_id = D.department_id
        WHERE 
            D.department_id = %s
            AND U.is_active = 1;
    """, (department_id,))

    supervisors = cur.fetchall()

    if (supervisors is None):
        return None
    else:
        supervisor_list = get_supervisor_list(supervisors)
        supervisors_with_supervisees = get_supervisors_with_supervisees(
            supervisor_list)

        return supervisors_with_supervisees


# get student supervisors
def get_student_supervisors():
    cur = getCursor()
    cur.execute("""
        SELECT
            student_id,
            supervisor_id,
            supervisor_type
        FROM student_supervisor
        WHERE is_active = 1;
    """)

    student_supervisors = cur.fetchall()

    if (student_supervisors is None):
        return None
    else:
        return get_student_supervisor_list(student_supervisors)


# get student supervisor by user id and student id
def get_student_supervisor_by_user_id(user_id, student_id):

    supervisor_id = get_supervisor_id(user_id)

    cur = getCursor()
    cur.execute("""
        SELECT
            student_id,
            supervisor_id,
            supervisor_type
        FROM student_supervisor
        WHERE is_active = 1
            AND supervisor_id = %s
            AND student_id = %s;
    """, (supervisor_id, student_id,))

    student_supervisor = cur.fetchone()

    if (student_supervisor is None):
        return None
    else:
        return get_student_supervisor(student_supervisor)


# get supervisor ids who have filled the 6MR form
def get_supervisor_ids_by_form_id(form_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            DISTINCT(S.supervisor_id)
        FROM supervisor S
        JOIN answer A ON A.answered_by = S.user_id
        WHERE A.form_id = %s;
    """, (form_id,))

    supervisor_ids = cur.fetchall()

    if supervisor_ids is None:
        return None
    else:
        return supervisor_ids
    

# update supervisor
def update_supervisor(supervisor: Supervisor):
    cur = getCursor()
    cur.execute("""
        UPDATE supervisor
        SET 
            first_name = %s,
            last_name = %s,
            phone = %s
        WHERE 
            supervisor_id = %s;
    """, (
        supervisor.first_name,
        supervisor.last_name,
        supervisor.phone,
        supervisor.supervisor_id
    ))


# get all supervisors
def get_all_supervisors():

    cursor = getCursor()
    cursor.execute("""
        SELECT 
            SV.user_id,
            SV.supervisor_id,
            '' AS supervisor_type,
            SV.first_name,
            SV.last_name,
            SV.phone,
            U.email,
            D.department_name
        FROM supervisor SV
        JOIN user U ON U.user_id = SV.user_id
        JOIN department D ON D.department_id = U.department_id
        WHERE U.is_active = 1;
        """)

    supervisors_select = cursor.fetchall()

    if (supervisors_select is None):
        return None
    else:
        supervisors_list = supervisors.get_supervisor_list(supervisors_select)
        supervisors_with_supervisees = get_supervisors_with_supervisees(
            supervisors_list)
        return supervisors_with_supervisees


# get supervisor (model)
def get_supervisor(supervisor):
    supervisor_model = Supervisor()

    supervisor_model.user_id = supervisor[0]
    supervisor_model.supervisor_id = supervisor[1]
    supervisor_model.supervisor_type = supervisor[2]
    supervisor_model.first_name = supervisor[3]
    supervisor_model.last_name = supervisor[4]
    supervisor_model.phone = supervisor[5]
    supervisor_model.email = supervisor[6]
    supervisor_model.department_name = supervisor[7]

    return supervisor_model


# get supervisors list (model)
def get_supervisor_list(supervisors):
    supervisor_list = []

    for supervisor in supervisors:
        supervisor_list.append(get_supervisor(supervisor))

    return supervisor_list


# get student supervisor (model)
def get_student_supervisor(student_supervisor):
    student_supervisor_model = StudentSupervisor()
    student_supervisor_model.student_id = student_supervisor[0]
    student_supervisor_model.supervisor_id = student_supervisor[1]
    student_supervisor_model.supervisor_type = student_supervisor[2]

    return student_supervisor_model


# get student supervisor list (model)
def get_student_supervisor_list(student_supervisors):
    student_supervisor_list = []

    for student_supervisor in student_supervisors:
        student_supervisor_list.append(
            get_student_supervisor(student_supervisor))

    return student_supervisor_list


# get supervisors with supervisees
def get_supervisors_with_supervisees(supervisors_list):

    student_supervisors = get_student_supervisors()

    supervisor_list = []

    for supervisor in supervisors_list:
        supervisor.supervisee_list = []

        for student_supervisor in student_supervisors:
            if (supervisor.supervisor_id == student_supervisor.supervisor_id):
                student_user_id = students.get_user_id(
                    student_supervisor.student_id)
                student = students.get_student_by_user_id(student_user_id)
                supervisor.supervisee_list.append(student)

        supervisor_list.append(supervisor)

    return supervisor_list


#get student current supervisors
def get_supervisors(student_id, supervisor_type):
    cur = getCursor()
    cur.execute("""
        SELECT 
            s.student_id, 
            supervisor_id, 
            supervisor_type, 
            CONCAT(first_name, " ", last_name)
        FROM student s 
        JOIN user st 
        USING(user_id)
        JOIN user su 
        USING(user_id)
        LEFT JOIN student_supervisor 
        USING (student_id) 
        JOIN supervisor 
        USING (supervisor_id)
        WHERE supervisor_type = %s
        AND student_id = %s;
    """, (supervisor_type, student_id))
    supervisors = cur.fetchall()
    return supervisors


#get supervisors from different department based on student
def get_supervisor_by_department(student_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            supervisor_id, 
            CONCAT(first_name, " ", last_name),
            department_id
        FROM supervisor 
        JOIN user
        USING (user_id) 
        WHERE department_id = (
            SELECT department_id 
            FROM user
            JOIN student 
            USING (user_id) 
            WHERE student_id=%s
        );
    """,(student_id,))   
    sup_list = cur.fetchall()
    return sup_list 


#delete student supervisor relationship
def student_supervisor_delete(student_id):
    cur = getCursor()
    cur.execute("""
        DELETE FROM student_supervisor
        WHERE student_id = %s 
    """,(student_id,))


# assign main supervisor 
def assign_main_supervisor(student_id, main_sup_id):
    cur=getCursor() 
    cur.execute("""
        INSERT INTO student_supervisor 
        VALUES (%s, %s, "principal", 1)
    """, (student_id, main_sup_id,))  


# assign co supervisors
def assign_co_supervisor(student_id, co_sup_id):
    cur=getCursor() 
    cur.execute("""
        INSERT INTO student_supervisor 
        VALUES (%s, %s, "co", 1)
    """, (student_id, co_sup_id,))      


