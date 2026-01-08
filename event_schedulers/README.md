# Event Scheduling & Resource Allocation System

## Goal
The goal of this application is to provide a platform where organizations can schedule events (workshops, seminars, classes) and allocate shared resources (rooms, instructors, equipment). The system ensures resource conflicts do not occur through custom-designed validation logic.

## Features
- **Event Management**: Create, edit, and view events with detailed descriptions and timing.
- **Resource Management**: Manage various resources that can be allocated to events.
- **Resource Allocation**: Assign specific resources to events while preventing overlaps.
- **Conflict Detection**: Automated verification of resource availability.
- **Reporting**: Generate utilization reports for resources within specific date ranges.
- **Role-Based Access Control (RBAC)**: Secure access with Admin and User roles.

## Database Design
The system is built on a relational database with the following primary tables:

### 1. Event
- `event_id`: Primary Key
- `title`: Name of the event
- `start_time`: Beginning of the event
- `end_time`: Conclusion of the event
- `description`: Detailed information about the event

### 2. Resource
- `resource_id`: Primary Key
- `resource_name`: Name of the resource
- `resource_type`: Type of resource (Room, Instructor, Equipment, etc.)

### 3. EventResourceAllocation
- `allocation_id`: Primary Key
- `event_id`: Foreign Key (references Event)
- `resource_id`: Foreign Key (references Resource)

## Views
- **Add/Edit/View Events**: Complete lifecycle management for event entities.
- **Add/Edit/View Resources**: Management of shared resources.
- **Allocate resources to events**: Interface to assign resources to specific events.
- **Conflict detection view**: Integrated into the event and allocation workflows to show and prevent booking issues.

## Logic Requirements

### Conflict Detection
Whenever an event is created/edited or a resource is allocated, the system verifies:
- **No double-booking**: A resource cannot be assigned to two events at the same time.
- **Time overlap handling**: Correctly identifies overlapping windows.
- **Edge cases**: Addresses various scenarios including:
    - `start = end` (Zero-duration windows)
    - Nested intervals (One event entirely within another)
    - Partial overlaps (Events that share a portion of time)

### Resource Utilization Report
Provides metrics based on a user-selected date range:
- **Resource**: Name of the resource.
- **Total Hours Utilized**: Sum of duration for all bookings within the range.
- **Bookings Count**: Number of times the resource was used.

## Use Cases Implemented
The application is validated against these core scenarios:
1. **Resource Creation**: Multiple resources (Rooms, Equipment) established.
2. **Event Creation**: Several events created with intentionally overlapping time windows.
3. **Allocation**: Resources successfully mapped to events.
4. **Conflict Validation**: System correctly errors out when trying to double-book a resource.
5. **Reporting**: Accurate computation of utilization metrics.

## Tech Stack
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Frontend**: HTML5, Vanilla CSS
- **Authentication**: Werkzeug (Password hashing)
- **Database Driver**: PyMySQL

## Getting Started

### Prerequisites
- Python 3.x
- MySQL Server

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Database Setup:
   - Create a database named `event_scheduler`.
   - Run `python setup_db.py` to initialize the schema and data.

### Running the App
```bash
python app.py
```
## Screenshots
![login page](login_page.png)
![event page](event_page.png)
![edit event](edit_event.png)
![resource page](resource_page.png)
![add resources 1](add_resources_1.png)
![add resources 2](add_resources_2.png)
![allocate resource](allocate_resource.png)
![resource utilization](resource_utilization.png)
![report generation](report_generation.png)
![report generation 2](report_generation_2.png)
![user login](user_login.png)

