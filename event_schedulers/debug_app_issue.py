import urllib.request
import urllib.error
import mysql.connector
from db import get_db_connection

def check_db():
    print("Checking Database Connection...")
    try:
        conn = get_db_connection()
        cwd = conn.cursor()
        cwd.execute("SELECT DATABASE()")
        db_name = cwd.fetchone()
        print(f"Connected to database: {db_name}")
        
        cwd.execute("SHOW TABLES")
        tables = cwd.fetchall()
        print("Tables found:", tables)
        
        conn.close()
        return True
    except Exception as e:
        print(f"FAILED to connect to DB: {e}")
        return False

def check_url(url):
    print(f"Checking URL: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            print(f"Status Code: {response.getcode()}")
            content = response.read(100) 
            print(f"Content snippet: {content}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"Error fetching URL: {e}")

if __name__ == "__main__":
    if check_db():
        check_url("http://127.0.0.1:5000/events")
