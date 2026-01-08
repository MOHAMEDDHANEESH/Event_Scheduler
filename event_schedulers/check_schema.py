import pymysql

def check_schema():
    conn = pymysql.connect(host="localhost", user="root", password="Dhaneesh@123", database="event_scheduler")
    cur = conn.cursor()
    cur.execute("DESCRIBE resource")
    for row in cur.fetchall():
        print(row)
    conn.close()

if __name__ == "__main__":
    check_schema()
