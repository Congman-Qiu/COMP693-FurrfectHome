import app.util.connect as connect
import mysql.connector

# Global Variables
dbconn = None

# Database connection
def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser,
                                             password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, autocommit=True)
        dbconn = connection.cursor(buffered=True)
        return dbconn
    else:
        return dbconn
