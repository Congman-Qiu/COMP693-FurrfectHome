from app.util import database
from app.models.admin_model import Admin


def getCursor():
    return database.getCursor()


# get admin details
def get_admin_details():
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            user_id,
            email
        FROM user
        WHERE user_type = 'administrator';
    """)

    admin = cursor.fetchone()

    if admin is None:
        return None
    else:
        admin_model = Admin()

        admin_model.user_id = admin[0]
        admin_model.email = admin[1]

        return admin_model
