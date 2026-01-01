import pymysql
import sys

print("Testing PyMySQL...")
try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Dhaneesh@123",
        database="event_scheduler"
    )
    print("PyMySQL connection successful!")
    conn.close()
except Exception as e:
    print(f"PyMySQL failed: {e}")
