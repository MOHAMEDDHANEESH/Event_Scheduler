import pymysql
import sys

def check_conflict():
    print("Connecting to DB...")
    try:
        conn = pymysql.connect(host="localhost", user="root", password="Dhaneesh@123", database="event_scheduler")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    cur = conn.cursor()
    
    print("Resetting DB...")
    cur.execute("DELETE FROM event_resource_allocation")
    cur.execute("DELETE FROM event")
    cur.execute("DELETE FROM resource")
    
    print("Inserting data...")
    cur.execute("INSERT INTO resource (resource_name, resource_type) VALUES ('Van 1', 'Vehicle')")
    r1 = cur.lastrowid
    
    cur.execute("INSERT INTO event (title, start_time, end_time, description) VALUES ('Trip A', '2025-01-01 10:00:00', '2025-01-01 11:00:00', 'Desc')")
    e1 = cur.lastrowid
    
    cur.execute("INSERT INTO event (title, start_time, end_time, description) VALUES ('Trip B', '2025-01-01 10:30:00', '2025-01-01 11:30:00', 'Desc')")
    e2 = cur.lastrowid
    
    print("Allocating Van 1 to Trip A...")
    cur.execute("INSERT INTO event_resource_allocation (event_id, resource_id) VALUES (%s, %s)", (e1, r1))
    conn.commit()
    
    print("Checking conflict for Van 1 on Trip B (Overlapping)...")
    cur.execute(
        """
        SELECT e.event_id FROM event e
        JOIN event_resource_allocation a ON e.event_id = a.event_id
        WHERE a.resource_id = %s
        AND e.start_time < (SELECT end_time FROM event WHERE event_id=%s)
        AND e.end_time > (SELECT start_time FROM event WHERE event_id=%s)
        """,
        (r1, e2, e2)
    )
    
    if cur.fetchone():
        print("PASS: Conflict detected correctly.")
    else:
        print("FAIL: No conflict detected for overlapping event!")
        
    conn.close()

if __name__ == "__main__":
    check_conflict()
