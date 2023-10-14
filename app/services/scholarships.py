from app.util import database
from app.models.scholarship_model import Scholarship


def getCursor():
    return database.getCursor()


# get all scholarships
def get_all_scholarships():
    cur = getCursor()
    cur.execute("""
        SELECT 
            SH.scholarship_id,
            SH.student_id,
            SH.scholarship_name,
            SH.value,
            SH.tenure,
            SH.end_date
        FROM scholarship SH
        WHERE SH.is_active = 1;
    """)

    scholarships = cur.fetchall()

    if (scholarships is None):
        return None
    else:
        return get_scholarship_list(scholarships)


# get scholarships by student id
def get_scholarships_by_student_id(student_id, is_active=1):
    cur = getCursor()
    cur.execute("""
        SELECT 
            SH.scholarship_id,
            SH.student_id,
            SH.scholarship_name,
            SH.value,
            SH.tenure,
            SH.end_date
        FROM scholarship SH
        JOIN student S ON S.student_id = SH.student_id
        WHERE 
            S.student_id = %s AND
            SH.is_active = %s;
        """, (student_id, is_active))

    scholarships = cur.fetchall()

    if (scholarships is None):
        return None
    else:
        return get_scholarship_list(scholarships)


# insert scholarship
def insert_scholarship(scholarship: Scholarship):
    cur = getCursor()
    cur.execute("""
                INSERT INTO scholarship (
                    scholarship_name, 
                    value, 
                    tenure, 
                    end_date, 
                    student_id,
                    is_active)
                VALUES (%s, %s, %s, %s, %s, 1)
    """, (
        scholarship.scholarship_name,
        scholarship.value,
        scholarship.tenure,
        scholarship.end_date,
        scholarship.student_id
    ))


# delete scholarship by student id
def delete_scholarship_by_student_id(student_id):
    cur = getCursor()
    cur.execute("""
        DELETE FROM scholarship
        WHERE student_id = %s 
    """, (student_id))


# get scholarships (model)
def get_scholarship(scholarships):
    scholarship_model = Scholarship()

    scholarship_model.scholarship_id = scholarships[0]
    scholarship_model.student_id = scholarships[1]
    scholarship_model.scholarship_name = scholarships[2]
    scholarship_model.value = scholarships[3]
    scholarship_model.tenure = scholarships[4]
    scholarship_model.end_date = scholarships[5]

    return scholarship_model


# get scholarship list (model)
def get_scholarship_list(scholarships):
    scholarship_list = []

    for item in scholarships:
        scholarship_list.append(get_scholarship(item))

    return scholarship_list
