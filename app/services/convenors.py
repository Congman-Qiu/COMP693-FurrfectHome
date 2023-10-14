from flask import session
from app.util import database
from app.models.convenor_model import Convenor


def getCursor():
    return database.getCursor()


# get convenor by user id
def get_convenor_by_user_id(user_id):
    cur = getCursor()
    cur.execute("""
        SELECT
            C.convenor_id,
            C.department_id,
            D.department_name,
            U.email,
            C.first_name,
            C.last_name
        FROM convenor C
        JOIN department D ON D.department_id = C.department_id
        JOIN user U ON U.user_id = C.user_id
        WHERE 
            U.is_active = 1 AND 
            U.user_id = %s;
    """, (user_id,))

    convenor = cur.fetchone()

    if (convenor is None):
        return None
    else:
        return get_convenor(convenor)


# get convenor user id
def get_convenor_user_id(convenor_id):
    cur = getCursor()
    cur.execute("""
        SELECT
            U.user_id
        FROM convenor C
        JOIN user U ON U.user_id = C.user_id
        WHERE 
            U.is_active = 1 AND 
            C.convenor_id = %s;
    """, (convenor_id,))

    user_id = cur.fetchone()

    if (user_id is None):
        return None
    else:
        return user_id[0]


# get convenor (model)
def get_convenor(convenor):
    convenor_model = Convenor()

    convenor_model.convenor_id = convenor[0]
    convenor_model.department_id = convenor[1]
    convenor_model.department_name = convenor[2]
    convenor_model.email = convenor[3]
    convenor_model.first_name = convenor[4]
    convenor_model.last_name = convenor[5]

    return convenor_model


# get convenor by department id
def get_convenor_by_department_id(department_id):
    cur = getCursor()
    cur.execute("""
        SELECT
            C.convenor_id,
            C.department_id,
            D.department_name,
            U.email,
            C.first_name,
            C.last_name
        FROM convenor C
        JOIN department D ON D.department_id = C.department_id
        JOIN user U ON U.user_id = C.user_id
        WHERE 
            U.is_active = 1 AND 
            C.department_id = %s;
    """, (department_id,))

    convenor = cur.fetchone()

    if (convenor is None):
        return None
    else:
        return get_convenor(convenor)