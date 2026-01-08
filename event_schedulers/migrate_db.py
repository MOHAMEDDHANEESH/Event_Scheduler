import pymysql

def migrate_db():
    conn = pymysql.connect(host="localhost", user="root", password="Dhaneesh@123", database="event_scheduler")
    cur = conn.cursor()
    print("Altering table resource to change resource_type to VARCHAR(50)...")
    try:
        cur.execute("ALTER TABLE resource MODIFY resource_type VARCHAR(50) NOT NULL")
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
