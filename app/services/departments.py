from app.models.student_model import Student
from app.util import database


def getCursor():
    return database.getCursor()


# get department id by student id
def get_department_id_by_student_id(student_id):
    cur = getCursor()
    cur.execute("""
        SELECT 
            U.department_id
        FROM student S
        JOIN user U ON U.user_id = S.user_id
        WHERE student_id = %s;
    """, (student_id,))
    department_id = cur.fetchone()

    if department_id is None:
        return None
    return department_id[0]


# get department id by user id
def get_department_id_by_user_id(user_id):
    cur = getCursor()
    cur.execute("""
        SELECT department_id
        FROM user
        WHERE user_id = %s
    """, (user_id,))
    department_id = cur.fetchall()

    return department_id[0]
