from app.models.employment_model import Employment
from app.util import database


def getCursor():
    return database.getCursor()


# get all employment
def get_all_employment():
    cur = getCursor()
    cur.execute("""
        SELECT 
            E.employment_id,
            E.student_id,
            E.employment_type,
            E.supervisor_name,
            E.hours_per_week
        FROM employment E
        WHERE E.is_active = 1;
    """)

    employment = cur.fetchall()

    if employment is None:
        return None
    else:
        return get_employment_list(employment)


# get employment by student id
def get_employment_by_student_id(student_id, is_active=1):
    cur = getCursor()
    cur.execute("""
        SELECT 
            E.employment_id,
            E.student_id,
            E.employment_type,
            E.supervisor_name,
            E.hours_per_week
        FROM employment E
        JOIN student S ON S.student_id = E.student_id
        WHERE 
            S.student_id = %s AND
            E.is_active = %s;
    """, (student_id, is_active))

    employment = cur.fetchall()

    if employment is None:
        return None
    else:
        return get_employment_list(employment)


# insert employment
def insert_employment(employment: Employment):
    cur = getCursor()
    cur.execute("""
                INSERT INTO employment (
                    student_id,
                    employment_type,
                    supervisor_name,
                    hours_per_week,
                    is_active
                    )
                VALUES (%s, %s, %s, %s, 1)
    """, (employment.student_id,
          employment.employment_type,
          employment.supervisor_name,
          employment.hours_per_week)
    )


# delete employment by student id
def delete_employment_by_student_id(student_id):
    cur = getCursor()
    cur.execute("""
        DELETE FROM employment
        WHERE student_id = %s 
    """, (student_id))


# get employment (model)
def get_employment(employment):
    employment_model = Employment()

    employment_model.employment_id = employment[0]
    employment_model.student_id = employment[1]
    employment_model.employment_type = employment[2]
    employment_model.supervisor_name = employment[3]
    employment_model.hours_per_week = employment[4]

    return employment_model


# get employment list (model)
def get_employment_list(employment):
    employment_list = []

    for item in employment:
        employment_list.append(get_employment(item))

    return employment_list
