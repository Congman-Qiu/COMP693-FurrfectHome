from app.models.student_model import Student
from app.util import database
from app.services import scholarships, employment, forms, supervisors


def getCursor():
    return database.getCursor()


# get student full name
def get_student_name(user_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            concat(student_first_name, " ", student_last_name ) AS full_name
        FROM student 
        JOIN user 
        USING (user_id)
        WHERE user_id = %s;
    """, (user_id,))
    student_name = cur.fetchall()
    return student_name


# get student user id by student id
def get_user_id(student_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            user_id
        FROM student 
        WHERE student_id = %s;
    """, (student_id,))
    user_id = cur.fetchone()

    if user_id is None:
        return None
    return user_id[0]


# get student by user id
def get_student_by_user_id(user_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT
            S.student_id,
            S.user_id,
            S.student_first_name,
            S.student_last_name,
            S.enrolment_date,
            S.address,
            S.phone,
            U.email,
            S.study_type,
            S.thesis_title,
            D.department_name,
            '' AS form_id
        FROM student S
        JOIN user U ON U.user_id = S.user_id
        JOIN department D ON D.department_id = U.department_id
        WHERE
            S.user_id = %s;
    """, (user_id,))

    student = cursor.fetchone()

    if student is None:
        return None
    else:
        return get_student(student)


# get students by department id
def get_students_by_department_id(department_id, search_term=None):
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            S.student_id
        FROM student S
        JOIN user U ON U.user_id = S.user_id
        JOIN department D ON D.department_id = U.department_id
        WHERE 
            U.department_id = %s;
    """, (department_id,))

    student_ids = cursor.fetchall()

    if student_ids is None:
        return None
    else:
        student_id_list = ', '.join(str(id[0]) for id in student_ids)
        student_id_tuple = tuple(student_id_list.split(', '))

        return get_students_with_employment_and_scholarships(search_term, student_id_tuple)


# get students by supervisor id
def get_students_by_supervisor_id(supervisor_id, search_term=None):
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            S.student_id
        FROM student S
        JOIN user U ON U.user_id = S.user_id
        JOIN student_supervisor SS ON SS.student_id = S.student_id
        JOIN supervisor SV ON SV.supervisor_id = SS.supervisor_id
        JOIN department D ON D.department_id = U.department_id
        WHERE 
            SV.supervisor_id = %s;
    """, (supervisor_id,))

    student_ids = cursor.fetchall()

    if student_ids is None:
        return None
    else:
        student_id_list = ', '.join(str(id[0]) for id in student_ids)
        student_id_tuple = tuple(student_id_list.split(', '))

        return get_students_with_employment_and_scholarships(search_term, student_id_tuple)


# get all students
def get_all_students(search_term=None):
    cursor = getCursor()
    cursor.execute("""SELECT student_id FROM student;""")

    student_ids = cursor.fetchall()

    if student_ids is None:
        return None
    else:
        student_id_list = ', '.join(str(id[0]) for id in student_ids)
        student_id_tuple = tuple(student_id_list.split(', '))
        
        return get_students_with_employment_and_scholarships(search_term, student_id_tuple)


# get unapproved students
def get_unapproved_students():
    cur = getCursor()
    cur.execute(
        """
            SELECT 
                S.student_id
            FROM student S
            JOIN user U
            ON S.user_id = U.user_id
            WHERE U.is_approved = 0;
        """
    )

    student_ids = cur.fetchall()

    if student_ids is None:
        return None
    else:
        student_id_list = ', '.join(str(id[0]) for id in student_ids)
        student_id_tuple = tuple(student_id_list.split(', '))
        
        return get_students_with_employment_and_scholarships(None, student_id_tuple)


# get students with employment and scholarships
def get_students_with_employment_and_scholarships(search_term=None, student_ids: tuple = None):

    search_query = "1 = 1"
    student_id_query = "S.student_id IN ('')"

    if search_term is not None and search_term != "":
        search_query = "S.student_id LIKE '%" + str(search_term) + \
            "%' OR CONCAT(S.student_first_name, ' ', S.student_last_name) LIKE '%" + \
            str(search_term) + "%'"

    if student_ids is not None and len(student_ids) > 0 and student_ids[0] != "":
        student_id_query = "S.student_id IN (" + ",".join(student_ids) + ")"

    cursor = getCursor()
    cursor.execute("""
        SELECT 
            S.student_id,
            S.user_id,
            S.student_first_name,
            S.student_last_name,
            S.enrolment_date,
            S.address,
            S.phone,
            U.email,
            S.study_type,
            S.thesis_title,
            D.department_name,
            F.form_id
        FROM student S
        JOIN user U ON U.user_id = S.user_id
        JOIN department D ON D.department_id = U.department_id
        LEFT JOIN form F ON F.created_user_id = S.user_id AND F.is_current = 1
        WHERE 
            U.is_active = 1 AND
            """ + search_query + """ AND
            """ + student_id_query + """;
    """)

    students = cursor.fetchall()

    if students is None:
        return None
    else:
        employment_list = employment.get_all_employment()
        scholarship_list = scholarships.get_all_scholarships()

        students_list = []

        for student in get_student_list(students):

            student.employment = []
            student.scholarships = []
            student.supervisors = []

            for emp in employment_list:
                if emp.student_id == student.student_id:
                    student.employment.append(emp)

            for scholarship in scholarship_list:
                if scholarship.student_id == student.student_id:
                    student.scholarships.append(scholarship)

            for sup in supervisors.get_supervisors_by_student_id(student.student_id):
                student.supervisors.append(sup)

            students_list.append(student)

        return students_list


# update existing student
def update_student(student: Student):
    cursor = getCursor()
    cursor.execute("""
        UPDATE student SET
            student_first_name = %s,
            student_last_name = %s,
            enrolment_date = %s,
            address = %s,
            phone = %s,
            study_type = %s,
            thesis_title = %s
        WHERE
            student_id = %s;
    """, (
        student.student_first_name,
        student.student_last_name,
        student.enrolment_date,
        student.address,
        student.phone,
        student.study_type,
        student.thesis_title,
        student.student_id
    ))


# insert new student
def insert_student(student: Student):
    cursor = getCursor()
    cursor.execute("""
        INSERT INTO student (
            user_id,
            student_first_name,
            student_last_name,
            enrolment_date,
            address,
            phone,
            study_type,
            thesis_title
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        );
    """, (
        student.user_id,
        student.student_first_name,
        student.student_last_name,
        student.enrolment_date,
        student.address,
        student.phone,
        student.study_type,
        student.thesis_title
    ))

    return cursor.lastrowid


# save student update or insert
def save_student(student: Student):

    existing_student = get_student_by_user_id(student.user_id)

    if existing_student is not None:
        existing_student.student_first_name = student.student_first_name if student.student_first_name is not None else existing_student.student_first_name
        existing_student.student_last_name = student.student_last_name if student.student_last_name is not None else existing_student.student_last_name
        existing_student.enrolment_date = student.enrolment_date if student.enrolment_date is not None else existing_student.enrolment_date
        existing_student.address = student.address if student.address is not None else existing_student.address
        existing_student.phone = student.phone if student.phone is not None else existing_student.phone
        existing_student.study_type = student.study_type if student.study_type is not None else existing_student.study_type
        existing_student.thesis_title = student.thesis_title if student.thesis_title is not None else existing_student.thesis_title

        cur = getCursor()
        cur.execute("""
            UPDATE student
            SET student_first_name = %s,
                student_last_name = %s,
                enrolment_date = %s,    
                address = %s,
                phone = %s,
                study_type = %s,
                thesis_title = %s
            WHERE user_id = %s 
        """, (
            existing_student.student_first_name,
            existing_student.student_last_name,
            existing_student.enrolment_date,
            existing_student.address,
            existing_student.phone,
            existing_student.study_type,
            existing_student.thesis_title,
            student.user_id
        )
        )

        return student
    else:
        cur = getCursor()
        cur.execute("""
            INSERT INTO student (
                user_id,
                student_first_name,
                student_last_name,
                enrolment_date,
                address,
                phone,
                study_type,
                thesis_title
            ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
            );
            """, (
            student.user_id,
            student.student_first_name,
            student.student_last_name,
            student.enrolment_date,
            student.address,
            student.phone,
            student.study_type,
            student.thesis_title
        ))

    return cur.lastrowid


# activate/ deactivate student
def activate_deactivate_student(student_id, is_active):
    # takes is_active arg as 1 or 0 for active and inactive status respectively
    query = """
            UPDATE user U
            JOIN student S ON S.user_id = U.user_id
            SET U.is_active = %s 
            WHERE S.student_id = %s;
        """

    cursor = getCursor()
    cursor.execute(query, (is_active, student_id,))


# approve/ unapprove student
def approve_reject_student(student_id, is_approved):
    # takes is_approved arg as 1 or 0 for approved and unapproved status respectively
    query = """
            UPDATE user U
            JOIN student S ON S.user_id = U.user_id
            SET U.is_approved = %s 
            WHERE S.student_id = %s;
        """

    cursor = getCursor()
    cursor.execute(query, (is_approved, student_id,))


# get student (model)
def get_student(student):
    student_model = Student()

    student_model.student_id = student[0]
    student_model.user_id = student[1]
    student_model.student_first_name = student[2]
    student_model.student_last_name = student[3]
    student_model.enrolment_date = student[4]
    student_model.address = student[5]
    student_model.phone = student[6]
    student_model.email = student[7]
    student_model.study_type = student[8]
    student_model.thesis_title = student[9]
    student_model.department_name = student[10]
    student_model.current_form_id = student[11]

    return student_model


# get student list (model)
def get_student_list(students):
    student_list = []

    for student in students:
        student_list.append(get_student(student))

    return student_list


# get student that has filled out section f and not completed by chair yet
def get_students_who_submitted_section_f():
    cur=getCursor()
    cur.execute("""
                SELECT
                    u.user_id,
                    a.student_id,
                    a.student_first_name,
                    a.student_last_name,
                    f.form_id,
                    (SELECT answer_value FROM answer WHERE form_id = f.form_id AND question_id = 86) AS answer_86,
                    (SELECT answer_value FROM answer WHERE form_id = f.form_id AND question_id = 87) AS answer_87,
                    (SELECT answer_value FROM answer WHERE form_id = f.form_id AND question_id = 88) AS answer_88,
                    d.department_name
                FROM student a
                LEFT JOIN form f ON a.user_id = f.created_user_id
                JOIN user u USING(user_id) 
					JOIN department d USING (department_id)
                WHERE u.is_approved = 1
                    AND f.is_student_submitted = 1
                    AND f.is_chair_completed = 0;

    """)
    students=cur.fetchall()
    return students    



