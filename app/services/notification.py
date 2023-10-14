from app.util import database


def getCursor():
    return database.getCursor()


# get a list of notifications for loggedin admin
def get_notifications_by_user_id(logged_in_user):
    cur = getCursor()
    cur.execute(
        """
            SELECT\
                t.notification_type,\
                DATE_FORMAT(n.created_date, '%d/%m/%Y'),\
                n.message FROM notification n\
            JOIN notification_type t\
            ON t.notification_type_id=n.notification_type_id\
            WHERE user_id = %s
        """, (
            logged_in_user,
        )
    )

    notifications_list = cur.fetchall()

    return notifications_list


# add new message to notification table
def create_notification(user_id, today_date, message):
    cur = getCursor()
    cur.execute(
        """
            INSERT INTO notification(\
                notification_type_id,\
                user_id,\
                created_date,\
                message,is_read,\
                is_active\
            )\
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            1,
            user_id,
            today_date,
            message,
            0,
            1
        )
    )
