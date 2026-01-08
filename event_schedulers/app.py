from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql.cursors

app = Flask(__name__)
app.secret_key = "secretkey"

USERS = {
    "Admin": {"password": generate_password_hash("Admin@123"), "role": "admin"},
    "User": {"password": generate_password_hash("User@123"), "role": "user"}
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please login to access this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please login to access this page.")
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash("Access denied. Admin privileges required.")
            return redirect(url_for('report'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]
        
        if user_id in USERS and check_password_hash(USERS[user_id]["password"], password):
            session['logged_in'] = True
            session['user_id'] = user_id
            session['role'] = USERS[user_id]["role"]
            flash("Login successful!")
            if USERS[user_id]["role"] == "admin":
                return redirect(url_for('events'))
            else:
                return redirect(url_for('report'))
        else:
            flash("Invalid User ID or Password!")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/events")
@admin_required
def events():
    db = get_db_connection()
    try:
        cur = db.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM event")
        events = cur.fetchall()
        
        for event in events:
            cur.execute("""
                SELECT era.allocation_id, r.resource_id, r.resource_name, r.resource_type
                FROM event_resource_allocation era
                JOIN resource r ON era.resource_id = r.resource_id
                WHERE era.event_id = %s
            """, (event['event_id'],))
            event['allocations'] = cur.fetchall()
            
            cur.execute("""
                SELECT DISTINCT e.event_id, e.title, e.start_time, e.end_time,
                       GROUP_CONCAT(DISTINCT r.resource_name SEPARATOR ', ') as conflicting_resources
                FROM event e
                JOIN event_resource_allocation era1 ON e.event_id = era1.event_id
                JOIN event_resource_allocation era2 ON era1.resource_id = era2.resource_id
                JOIN resource r ON era1.resource_id = r.resource_id
                WHERE era2.event_id = %s
                AND e.event_id != %s
                AND e.start_time < %s
                AND e.end_time > %s
                GROUP BY e.event_id, e.title, e.start_time, e.end_time
            """, (event['event_id'], event['event_id'], event['end_time'], event['start_time']))
            event['resource_conflicts'] = cur.fetchall()
            
            cur.execute("""
                SELECT event_id, title, start_time, end_time
                FROM event
                WHERE event_id != %s
                AND start_time < %s
                AND end_time > %s
            """, (event['event_id'], event['end_time'], event['start_time']))
            event['overlapping_events'] = cur.fetchall()
        
        return render_template("events.html", events=events)
    finally:
        db.close()

@app.route("/events/add", methods=["GET", "POST"])
@admin_required
def add_event():
    if request.method == "POST":
        title = request.form["title"]
        start = request.form["start"]
        end = request.form["end"]
        desc = request.form["description"]

        db = get_db_connection()
        try:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO event (title, start_time, end_time, description) VALUES (%s,%s,%s,%s)",
                (title, start, end, desc)
            )
            db.commit()
            return redirect(url_for("events"))
        finally:
            db.close()

    return render_template("add_event.html")

@app.route("/events/edit/<int:event_id>", methods=["GET", "POST"])
@admin_required
def edit_event(event_id):
    db = get_db_connection()
    try:
        cur = db.cursor(pymysql.cursors.DictCursor)
        
        if request.method == "POST":
            title = request.form["title"]
            start = request.form["start"]
            end = request.form["end"]
            desc = request.form["description"]

            cur.execute("SELECT resource_id FROM event_resource_allocation WHERE event_id = %s", (event_id,))
            allocated_resources = [row['resource_id'] for row in cur.fetchall()]
            
            conflict = False
            for res_id in allocated_resources:
                cur.execute(
                    """
                    SELECT e.event_id FROM event e
                    JOIN event_resource_allocation a ON e.event_id = a.event_id
                    WHERE a.resource_id = %s
                    AND e.event_id != %s
                    AND e.start_time < %s
                    AND e.end_time > %s
                    """,
                    (res_id, event_id, end, start)
                )
                if cur.fetchone():
                    conflict = True
                    break
            
            if conflict:
                flash("Cannot update: Resource conflict detected with existing allocations.")
            else:
                cur.execute(
                    "UPDATE event SET title=%s, start_time=%s, end_time=%s, description=%s WHERE event_id=%s",
                    (title, start, end, desc, event_id)
                )
                db.commit()
                return redirect(url_for("events"))

        cur.execute("SELECT * FROM event WHERE event_id = %s", (event_id,))
        event = cur.fetchone()
        return render_template("edit_event.html", event=event)
    finally:
        db.close()

@app.route("/events/delete/<int:event_id>")
@admin_required
def delete_event(event_id):
    db = get_db_connection()
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM event_resource_allocation WHERE event_id = %s", (event_id,))
        cur.execute("DELETE FROM event WHERE event_id = %s", (event_id,))
        db.commit()
        flash("Event deleted successfully!")
    finally:
        db.close()
    return redirect(url_for("events"))

@app.route("/resources")
@admin_required
def resources():
    db = get_db_connection()
    try:
        cur = db.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM resource")
        resources = cur.fetchall()
        return render_template("resources.html", resources=resources)
    finally:
        db.close()

@app.route("/resources/add", methods=["GET", "POST"])
@admin_required
def add_resource():
    if request.method == "POST":
        name = request.form["name"]
        rtype = request.form["type"]

        db = get_db_connection()
        try:
            cur = db.cursor(pymysql.cursors.DictCursor)
            
            cur.execute(
                "SELECT * FROM resource WHERE resource_name = %s AND resource_type = %s",
                (name, rtype)
            )
            existing = cur.fetchone()
            
            if existing:
                flash(f"Resource '{name}' with type '{rtype}' already exists!")
            else:
                cur.execute(
                    "INSERT INTO resource (resource_name, resource_type) VALUES (%s,%s)",
                    (name, rtype)
                )
                db.commit()
                flash("Resource added successfully!")
                return redirect(url_for("resources"))
        finally:
            db.close()

    return render_template("add_resource.html")

@app.route("/resources/edit/<int:resource_id>", methods=["GET", "POST"])
@admin_required
def edit_resource(resource_id):
    db = get_db_connection()
    try:
        cur = db.cursor(pymysql.cursors.DictCursor)
        
        if request.method == "POST":
            name = request.form["name"]
            rtype = request.form["type"]
            
            cur.execute(
                "UPDATE resource SET resource_name=%s, resource_type=%s WHERE resource_id=%s",
                (name, rtype, resource_id)
            )
            db.commit()
            return redirect(url_for("resources"))

        cur.execute("SELECT * FROM resource WHERE resource_id = %s", (resource_id,))
        resource = cur.fetchone()
        return render_template("edit_resource.html", resource=resource)
    finally:
        db.close()

@app.route("/resources/delete/<int:resource_id>")
@admin_required
def delete_resource(resource_id):
    db = get_db_connection()
    try:
        cur = db.cursor(pymysql.cursors.DictCursor)
        
        cur.execute(
            "SELECT e.title FROM event_resource_allocation era JOIN event e ON era.event_id = e.event_id WHERE era.resource_id = %s",
            (resource_id,)
        )
        allocations = cur.fetchall()
        
        if allocations:
            event_titles = ", ".join([a['title'] for a in allocations])
            flash(f"Cannot delete: Resource is allocated to event(s): {event_titles}. De-allocate first.")
        else:
            cur.execute("DELETE FROM resource WHERE resource_id = %s", (resource_id,))
            db.commit()
            flash("Resource deleted successfully!")
    finally:
        db.close()
    return redirect(url_for("resources"))

@app.route("/allocate", methods=["GET", "POST"])
@admin_required
def allocate():
    db = get_db_connection()
    try:
        cur = db.cursor(pymysql.cursors.DictCursor)

        cur.execute("SELECT * FROM event")
        events = cur.fetchall()

        cur.execute("SELECT * FROM resource")
        resources = cur.fetchall()

        if request.method == "POST":
            event_id = request.form["event"]
            resource_id = request.form["resource"]

            cur.execute(
                """
                SELECT e.title FROM event e
                JOIN event_resource_allocation a ON e.event_id = a.event_id
                WHERE a.resource_id = %s
                AND e.start_time < (SELECT end_time FROM event WHERE event_id=%s)
                AND e.end_time > (SELECT start_time FROM event WHERE event_id=%s)
                """,
                (resource_id, event_id, event_id)
            )

            conflict = cur.fetchone()
            if conflict:
                flash(f"Invalid Allocation: Resource is already booked by event '{conflict['title']}' during this time.")
            else:
                cur.execute(
                    "INSERT INTO event_resource_allocation (event_id, resource_id) VALUES (%s,%s)",
                    (event_id, resource_id)
                )
                db.commit()
                flash("Resource allocated successfully")

        return render_template("allocate.html", events=events, resources=resources)
    finally:
        db.close()

@app.route("/events/deallocate/<int:allocation_id>")
@admin_required
def deallocate(allocation_id):
    db = get_db_connection()
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM event_resource_allocation WHERE allocation_id = %s", (allocation_id,))
        db.commit()
        flash("Resource de-allocated successfully")
    finally:
        db.close()
    return redirect(url_for("events"))

@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    data = []
    if request.method == "POST":
        start = request.form["start"]
        end = request.form["end"]

        db = get_db_connection()
        try:
            cur = db.cursor(pymysql.cursors.DictCursor)
            cur.execute(
                """
                SELECT r.resource_name,
                       SUM(TIMESTAMPDIFF(HOUR, e.start_time, e.end_time)) AS total_hours,
                       COUNT(e.event_id) AS bookings
                FROM resource r
                JOIN event_resource_allocation a ON r.resource_id = a.resource_id
                JOIN event e ON a.event_id = e.event_id
                WHERE e.start_time BETWEEN %s AND %s
                GROUP BY r.resource_id
                """,
                (start, end)
            )
            data = cur.fetchall()
        finally:
            db.close()

    return render_template("report.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)


   