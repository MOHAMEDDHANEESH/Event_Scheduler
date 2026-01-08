import pymysql
import pymysql.cursors

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Dhaneesh@123",
        database="event_scheduler"
    )

def reset_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM event_resource_allocation")
    cur.execute("DELETE FROM event")
    cur.execute("DELETE FROM resource")
    conn.commit()
    return conn

def reproduce():
    conn = reset_db()
    cur = conn.cursor()
    
    print("1. Creating Resource R1")
    cur.execute("INSERT INTO resource (resource_name, resource_type) VALUES ('Test Van', 'Vehicle')")
    r1_id = cur.lastrowid
    
    print("2. Creating Event E1 (10:00 - 11:00)")
    cur.execute("INSERT INTO event (title, start_time, end_time, description) VALUES ('E1', '2025-01-01 10:00:00', '2025-01-01 11:00:00', 'Desc')")
    e1_id = cur.lastrowid
    
    print("3. Creating Event E2 (10:30 - 11:30) [Overlaps E1]")
    cur.execute("INSERT INTO event (title, start_time, end_time, description) VALUES ('E2', '2025-01-01 10:30:00', '2025-01-01 11:30:00', 'Desc')")
    e2_id = cur.lastrowid
    
    print("4. Allocating R1 to E1")
    cur.execute("INSERT INTO event_resource_allocation (event_id, resource_id) VALUES (%s, %s)", (e1_id, r1_id))
    conn.commit()
    
    print("5. Checking conflict for R1 on E2 (Simulating app.py query)")
    query = """
            SELECT e.event_id FROM event e
            JOIN event_resource_allocation a ON e.event_id = a.event_id
            WHERE a.resource_id = %s
            AND e.start_time < (SELECT end_time FROM event WHERE event_id=%s)
            AND e.end_time > (SELECT start_time FROM event WHERE event_id=%s)
            """
    cur.execute(query, (r1_id, e2_id, e2_id))
    conflict = cur.fetchone()
    
    if conflict:
        print(f"SUCCESS: Conflict detected with Event {conflict[0]}")
    else:
        print("FAILURE: No conflict detected!")

    conn.close()

if __name__ == "__main__":
    reproduce()
