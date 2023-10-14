from app.util import database
from app.models.user_model import User
from app.models.student_model import Student
from app.services import students, scholarships, employment, supervisors
import bcrypt


def getCursor():
    return database.getCursor()


# get user account by email and password
def get_user_account(email, password=""):
    message = None

    user = get_user_by_email(email)

    if user is not None:
        # if email exists
        db_password = user[3]

        if bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
            # if password matches
            if user[6] == 0:
                # if account is not approved by admin yet
                message = "Account is not approved yet"
            elif user[5] == 0:
                # if account is inactive
                message = "Account is inactive"
            return user, message
        else:
            # if password does not match
            message = "Invalid password"

    else:
        # if email does not exist
        message = "Email does not exist"

    return user, message


# get user by email
def get_user_by_email(email):
    cur = getCursor()
    cur.execute(
        """
            SELECT 
                user_id,
                email,
                user_type,
                password,
                department_id, 
                is_active,
                is_approved
            FROM 
                user 
            WHERE 
                email = %s;
        """,
        (email,)
    )

    user = cur.fetchone()

    return user


# save new user to user table
def save_user(user: User):
    email = user.email
    password = user.password
    user_type = user.user_type
    department = user.department

    cur = getCursor()
    cur.execute(
        """
            INSERT INTO user (
                email,
                user_type,
                password,
                department_id,
                is_active,
                is_approved
            )
            VALUES (
                %s,%s,%s,%s,%s,%s
            );
        """,
        (email, user_type, password, department, 1, 0, )
    )

    return cur.lastrowid  # newly inserted user id


# BELOW FUNCTIONS ARE USED FOR TESTING PURPOSES ONLY


# get test email address from config
def get_test_email():
    cur = getCursor()
    cur.execute(
        """
            SELECT 
                config_value
            FROM 
                config
            WHERE 
                config_type = 'test_email';
        """
    )

    test_email = cur.fetchone()

    return test_email[0]


# update test email address in config
def update_test_email(email):
    cur = getCursor()
    cur.execute(
        """
            UPDATE 
                config
            SET 
                config_value = %s
            WHERE 
                config_type = 'test_email';
        """,
        (email,)
    )