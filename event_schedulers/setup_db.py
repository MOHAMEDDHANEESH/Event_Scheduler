import pymysql
import os

def init_db():
    print("Initializing database...")
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Dhaneesh@123"
        )
        cursor = conn.cursor()

        with open("d:\\projects\\Airele Project\\event_scheduler\\schema.sql", "r") as f:
            schema_sql = f.read()

        statements = schema_sql.split(';')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        print("Database initialized successfully!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
