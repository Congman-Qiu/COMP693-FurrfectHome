from app.util import database
from app.models.chair_model import Chair


def getCursor():
    return database.getCursor()


# get chair details
def get_chair_details():
    cursor = getCursor()
    cursor.execute("""
        SELECT 
            C.user_id,
            C.chair_id,
            U.email
        FROM chair C
        JOIN user U ON U.user_id = C.user_id
        WHERE C.is_active = 1;
    """)

    chair = cursor.fetchone()

    if chair is None:
        return None
    else: 
        chair_model = Chair()
        
        chair_model.user_id = chair[0]
        chair_model.chair_id = chair[1]
        chair_model.email = chair[2]

        return chair_model