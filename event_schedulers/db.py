import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Dhaneesh@123",
        database="event_scheduler"
    )
