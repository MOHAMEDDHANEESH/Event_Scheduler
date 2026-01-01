import sys
print("Starting DB Debug Script")
try:
    import mysql.connector
    print("Imported mysql.connector")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

try:
    print("Attempting connection...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dhaneesh@123",
        database="event_scheduler"
    )
    print(f"Connection successful: {conn.is_connected()}")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
except SystemExit:
    print("SystemExit caught")
except:
    print("Unknown error caught")
