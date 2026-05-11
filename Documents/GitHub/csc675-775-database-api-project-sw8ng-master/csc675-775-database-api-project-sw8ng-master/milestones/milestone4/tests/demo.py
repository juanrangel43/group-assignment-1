#!/usr/bin/env python3
import sys
import os
import random
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.models import (
    User, Incident_Report, Incident_Status, Report_Category,
    Priority_Level, Weather, Data_Feed
)
from api.db_connectors import MySQL

_active_user_id = None

# ------------------------------------------------------------
# Ensure lookup tables have required rows
# ------------------------------------------------------------
def ensure_lookups():
    if not Report_Category.query(name="Delay"):
        Report_Category.create(name="Delay", description="Train delay", escalation_flag=0)
    if not Incident_Status.query(name="Reported"):
        Incident_Status.create(name="Reported", description="Initial report", display_order=1)
    if not Incident_Status.query(name="In-Progress"):
        Incident_Status.create(name="In-Progress", description="Being handled", display_order=2)
    if not Incident_Status.query(name="Resolved"):
        Incident_Status.create(name="Resolved", description="Completed", display_order=3)
    if not Priority_Level.query(name="Medium"):
        Priority_Level.create(name="Medium", description="Medium urgency", severity_rank=2)
    feed = Data_Feed.query(feed_name="Demo Feed")
    if not feed:
        feed = Data_Feed.create(feed_name="Demo Feed", feed_type="Demo")
    else:
        feed = feed[0]
    if not Weather.query(status="Clear"):
        Weather.create(feed_id=feed.feed_Id, status="Clear", temperature=20.0, recorded_timestamp=datetime.now())

# ------------------------------------------------------------
# User management (unchanged)
# ------------------------------------------------------------
def create_user():
    print("\n--- Create New User ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    email = input("Email: ").strip()
    first = input("First name: ").strip()
    last = input("Last name: ").strip()
    try:
        user = User.create(username=username, password=password, email=email,
                           first_name=first, last_name=last)
        print(f"User created! ID: {user.user_id}, Name: {user.first_name} {user.last_name}")
        global _active_user_id
        _active_user_id = user.user_id
        print(f"Active user set to: {user.username}")
    except Exception as e:
        print(f"Error: {e}")

def set_active_user():
    global _active_user_id
    list_users()
    uid = input("Enter User ID to set as active (0 to cancel): ").strip()
    try:
        uid = int(uid)
        if uid == 0:
            return
        user = User.get(uid)
        if user:
            _active_user_id = uid
            print(f"Active user set to: {user.username} (ID {uid})")
        else:
            print("User not found.")
    except:
        print("Invalid input.")

def get_active_user():
    global _active_user_id
    if _active_user_id is None:
        print("No active user set. Please create a user or set one (options 1 & 2).")
        return None
    user = User.get(_active_user_id)
    if not user:
        print("Active user no longer exists.")
        _active_user_id = None
        return None
    return user

def list_users():
    users = User.all()
    if not users:
        print("No users found.")
        return
    print("\n--- All Users ---")
    for u in users:
        print(f"ID: {u.user_id}, Username: {u.username}, Name: {u.first_name} {u.last_name}")

def delete_user():
    list_users()
    uid = input("Enter User ID to delete (0 to cancel): ").strip()
    try:
        uid = int(uid)
        if uid == 0:
            return
        user = User.get(uid)
        if not user:
            print("User not found.")
            return
        confirm = input(f"Delete user '{user.username}'? (y/n): ").strip().lower()
        if confirm == 'y':
            User.delete(uid)
            print(f"User {uid} deleted.")
            global _active_user_id
            if _active_user_id == uid:
                _active_user_id = None
                print("Active user cleared.")
        else:
            print("Cancelled.")
    except:
        print("Invalid input.")

# ------------------------------------------------------------
# Incident listing
# ------------------------------------------------------------
def list_incidents():
    incidents = Incident_Report.all()
    if not incidents:
        print("No incidents found.")
        return
    print("\n--- All Incidents ---")
    for inc in incidents:
        status_name = inc.status.name if inc.status else "None"
        print(f"ID: {inc.incident_id} | Status: {status_name} | Description: {inc.description[:50]}...")

# ------------------------------------------------------------
# Trip and delay propagation
# ------------------------------------------------------------
def list_trips():
    conn, cursor = MySQL.instance()
    try:
        cursor.execute("SELECT trip_id, scheduled_start, scheduled_end, trip_status FROM Trip")
        trips = cursor.fetchall()
        if not trips:
            print("No trips found. Please run demo_data.sql first.")
            return []
        print("\nAvailable Trips:")
        for t in trips:
            print(f"  ID: {t['trip_id']} | Start: {t['scheduled_start']} | Status: {t['trip_status']}")
        return trips
    finally:
        cursor.close()
        conn.close()

def show_trip_details(trip_id):
    conn, cursor = MySQL.instance()
    try:
        cursor.execute("SELECT scheduled_start, scheduled_end, trip_status FROM Trip WHERE trip_id = %s", (trip_id,))
        trip_row = cursor.fetchone()
        if not trip_row:
            print(f"Trip {trip_id} not found.")
            return
        print(f"\nTrip ID: {trip_id}")
        print(f"Start: {trip_row['scheduled_start']}, End: {trip_row['scheduled_end']}, Status: {trip_row['trip_status']}")

        cursor.execute("""
            SELECT st.stop_id, s.name, st.scheduled_arrival, st.scheduled_departure, st.sequence_number
            FROM Stop st
            JOIN Station s ON st.station_id = s.station_id
            WHERE st.trip_id = %s
            ORDER BY st.sequence_number
        """, (trip_id,))
        stops = cursor.fetchall()
        if not stops:
            print("No stops for this trip.")
            return

        cursor.execute("""
            SELECT stop_id, SUM(delay_minutes) AS total_delay
            FROM Delay_Propagation
            WHERE trip_id = %s
            GROUP BY stop_id
        """, (trip_id,))
        # Convert Decimal to int
        delays = {}
        for row in cursor.fetchall():
            delays[row['stop_id']] = int(row['total_delay'])   # fix Decimal conversion

        print("Stops:")
        for stop in stops:
            stop_id = stop['stop_id']
            total_delay = delays.get(stop_id, 0)
            scheduled_arr = stop['scheduled_arrival']
            scheduled_dep = stop['scheduled_departure']
            if total_delay > 0:
                est_arr = scheduled_arr + timedelta(minutes=total_delay)
                est_dep = scheduled_dep + timedelta(minutes=total_delay)
                print(f"  {stop['name']}: scheduled arrival {scheduled_arr}, departure {scheduled_dep}")
                print(f"      estimated arrival {est_arr}, departure {est_dep} (+{total_delay} min)")
            else:
                print(f"  {stop['name']}: arrival {scheduled_arr}, departure {scheduled_dep}")
    except Exception as e:
        print(f"Error in show_trip_details: {e}")
    finally:
        cursor.close()
        conn.close()

def get_trip_status(trip_id):
    conn, cursor = MySQL.instance()
    try:
        cursor.execute("SELECT trip_status FROM Trip WHERE trip_id = %s", (trip_id,))
        row = cursor.fetchone()
        return row['trip_status'] if row else None
    finally:
        cursor.close()
        conn.close()

def refresh_trip_status(trip_id):
    """Call the stored procedure that updates trip status based on delays."""
    conn, cursor = MySQL.instance()
    try:
        cursor.callproc("sp_refresh_trip_status", (trip_id,))
        conn.commit()
    except Exception as e:
        print(f"Warning: Could not refresh trip status: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_random_delay():
    user = get_active_user()
    if not user:
        return
    conn, cursor = MySQL.instance()
    try:
        cursor.execute("SELECT trip_id FROM Trip")
        trips = cursor.fetchall()
        if not trips:
            print("No trips found.")
            return
        trip = random.choice(trips)
        trip_id = trip['trip_id']

        cursor.execute("""
            SELECT st.stop_id, s.name, st.sequence_number
            FROM Stop st
            JOIN Station s ON st.station_id = s.station_id
            WHERE st.trip_id = %s
            ORDER BY st.sequence_number
        """, (trip_id,))
        stops = cursor.fetchall()
        if not stops:
            print("No stops for this trip.")
            return
        stop = random.choice(stops)
        delay_mins = random.randint(15, 45)   # ensure delay ≥15 to trigger trip status change

        cat = Report_Category.query(name="Delay")[0]
        stat = Incident_Status.query(name="Reported")[0]
        pri = Priority_Level.query(name="Medium")[0]
        weather = Weather.query(status="Clear")[0]
        incident = Incident_Report.create(
            user_id=user.user_id,
            description=f"Random delay of {delay_mins} minutes at {stop['name']}",
            category_id=cat.category_id,
            status_id=stat.status_id,
            priority_id=pri.priority_id,
            weather_id=weather.weather_id,
            reported_timestamp=datetime.now(),
            incident_source="CLI (random)"
        )
        print(f"\nIncident #{incident.incident_id} created: {delay_mins} min delay at {stop['name']} (Trip {trip_id})")
        print(f"  Description: {incident.description}")
        print(f"  Category: {incident.category.name}, Priority: {incident.priority.name}, Status: {incident.status.name}")

        cursor.callproc("Delay_Propagation", (incident.incident_id, trip_id, stop['stop_id'], delay_mins))
        conn.commit()
        print("Delay propagation executed.")

        cursor.execute("""
            SELECT d.delay_minutes, d.impact_scope, s.name
            FROM Delay_Propagation d
            JOIN Stop st ON d.stop_id = st.stop_id
            JOIN Station s ON st.station_id = s.station_id
            WHERE d.trip_id = %s
            ORDER BY st.sequence_number
        """, (trip_id,))
        delays = cursor.fetchall()
        if delays:
            print("\nPropagated delays (cumulative):")
            for d in delays:
                print(f"  {d['name']}: +{d['delay_minutes']} min")
        else:
            print("No downstream stops (delay at last stop).")

        # Show updated trip status
        new_status = get_trip_status(trip_id)
        print(f"\nTrip {trip_id} status is now: {new_status}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------
# View/Update incident status (clears identity map cache)
# ------------------------------------------------------------
def fresh_incident(inc_id):
    key = Incident_Report.identity_key(inc_id)
    if key in Incident_Report._identity_map:
        del Incident_Report._identity_map[key]
    return Incident_Report.get(inc_id)

def update_incident_workflow():
    inc_id = input("Enter Incident ID: ").strip()
    try:
        inc_id = int(inc_id)
    except:
        print("Invalid ID.")
        return

    inc = fresh_incident(inc_id)
    if not inc:
        print("Incident not found.")
        return

    print(f"\n--- Incident Report #{inc.incident_id} ---")
    print(f"Description: {inc.description}")
    print(f"Reported at: {inc.reported_timestamp}")
    print(f"Source: {inc.incident_source}")
    print(f"Category: {inc.category.name if inc.category else 'N/A'}")
    print(f"Priority: {inc.priority.name if inc.priority else 'N/A'}")
    print(f"Status: {inc.status.name if inc.status else 'N/A'}")
    print(f"Weather: {inc.weather.status if inc.weather else 'N/A'}")
    print(f"Reporter user ID: {inc.user_id}")
    print("------------------------------------")

    if inc.status.name == "Reported":
        print("\nNext allowed status: In-Progress")
        ans = input("Move to In-Progress? (y/n): ").strip().lower()
        if ans == 'y':
            new_status = Incident_Status.query(name="In-Progress")[0]
            inc.status_id = new_status.status_id
            inc.save()
            print("Status updated to In-Progress.")
            inc = fresh_incident(inc_id)
            print(f"Current status now: {inc.status.name}")
            ans2 = input("Move to Resolved? (y/n): ").strip().lower()
            if ans2 == 'y':
                resolved = Incident_Status.query(name="Resolved")[0]
                inc.status_id = resolved.status_id
                inc.save()
                print("Status updated to Resolved.")
                inc = fresh_incident(inc_id)
                print(f"Current status now: {inc.status.name}")
                del_ans = input("Delete delay propagation records for this incident? (y/n): ").strip().lower()
                if del_ans == 'y':
                    conn, cursor = MySQL.instance()
                    try:
                        cursor.execute("DELETE FROM Delay_Propagation WHERE incident_id = %s", (inc_id,))
                        conn.commit()
                        print(f"Deleted delay propagation records for incident {inc_id}.")
                        # Update trip status for all trips affected by this incident
                        cursor.execute("SELECT DISTINCT trip_id FROM Delay_Propagation WHERE incident_id = %s", (inc_id,))
                        trip_rows = cursor.fetchall()
                        for row in trip_rows:
                            trip_id = row['trip_id']
                            # Directly update trip status based on remaining delays
                            cursor.execute("""
                                UPDATE Trip
                                SET trip_status = CASE
                                    WHEN (SELECT COUNT(*) FROM Delay_Propagation WHERE trip_id = %s) = 0
                                    THEN 'Scheduled'
                                    ELSE 'Delayed'
                                END
                                WHERE trip_id = %s
                            """, (trip_id, trip_id))
                            conn.commit()
                            new_status = get_trip_status(trip_id)
                            print(f"Trip {trip_id} status is now: {new_status}")
                    except Exception as e:
                        print(f"Error: {e}")
                    finally:
                        cursor.close()
                        conn.close()
                else:
                    print("Delay records kept.")
            else:
                print("Workflow paused. Incident remains In-Progress.")
        else:
            print("Status unchanged.")
    elif inc.status.name == "In-Progress":
        # Similar logic as above, but shorter: allow resolution and deletion
        ans = input("Move to Resolved? (y/n): ").strip().lower()
        if ans == 'y':
            resolved = Incident_Status.query(name="Resolved")[0]
            inc.status_id = resolved.status_id
            inc.save()
            print("Status updated to Resolved.")
            inc = fresh_incident(inc_id)
            print(f"Current status now: {inc.status.name}")
            del_ans = input("Delete delay propagation records for this incident? (y/n): ").strip().lower()
            if del_ans == 'y':
                conn, cursor = MySQL.instance()
                try:
                    cursor.execute("DELETE FROM Delay_Propagation WHERE incident_id = %s", (inc_id,))
                    conn.commit()
                    print(f"Deleted delay propagation records for incident {inc_id}.")
                    cursor.execute("SELECT DISTINCT trip_id FROM Delay_Propagation WHERE incident_id = %s", (inc_id,))
                    trip_rows = cursor.fetchall()
                    for row in trip_rows:
                        trip_id = row['trip_id']
                        cursor.execute("""
                            UPDATE Trip
                            SET trip_status = CASE
                                WHEN (SELECT COUNT(*) FROM Delay_Propagation WHERE trip_id = %s) = 0
                                THEN 'Scheduled'
                                ELSE 'Delayed'
                            END
                            WHERE trip_id = %s
                        """, (trip_id, trip_id))
                        conn.commit()
                        new_status = get_trip_status(trip_id)
                        print(f"Trip {trip_id} status is now: {new_status}")
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            else:
                print("Delay records kept.")
        else:
            print("Status unchanged.")
    elif inc.status.name == "Resolved":
        print("Incident already resolved. No further transitions allowed.")
        del_ans = input("Delete delay propagation records for this incident? (y/n): ").strip().lower()
        if del_ans == 'y':
            conn, cursor = MySQL.instance()
            try:
                cursor.execute("DELETE FROM Delay_Propagation WHERE incident_id = %s", (inc_id,))
                conn.commit()
                print(f"Deleted delay propagation records for incident {inc_id}.")
                cursor.execute("SELECT DISTINCT trip_id FROM Delay_Propagation WHERE incident_id = %s", (inc_id,))
                trip_rows = cursor.fetchall()
                for row in trip_rows:
                    trip_id = row['trip_id']
                    cursor.execute("""
                        UPDATE Trip
                        SET trip_status = CASE
                            WHEN (SELECT COUNT(*) FROM Delay_Propagation WHERE trip_id = %s) = 0
                            THEN 'Scheduled'
                            ELSE 'Delayed'
                        END
                        WHERE trip_id = %s
                    """, (trip_id, trip_id))
                    conn.commit()
                    new_status = get_trip_status(trip_id)
                    print(f"Trip {trip_id} status is now: {new_status}")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            print("Delay records kept.")
    else:
        print("Cannot update this incident (unknown or cancelled).")

# ------------------------------------------------------------
# Main menu
# ------------------------------------------------------------
def main():
    print("\n=== Transit Incident System Demo ===")
    ensure_lookups()

    if not User.all():
        print("\nNo users found. Please create a user (will be set as active).")
        create_user()
        if not _active_user_id:
            print("Cannot proceed. Exiting.")
            return

    while True:
        print("\n=== Main Menu ===")
        print("1. Create a new user")
        print("2. Set active user")
        print("3. List all users")
        print("4. Delete a user")
        print("5. View trips (with estimated times if delayed)")
        print("6. Generate random delay")
        print("7. View/Update incident status")
        print("8. List all incidents")
        print("9. Exit")
        choice = input("Choose: ").strip()

        if choice == '1':
            create_user()
        elif choice == '2':
            set_active_user()
        elif choice == '3':
            list_users()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            trips = list_trips()
            if trips:
                tid = input("Enter Trip ID to view details: ").strip()
                try:
                    show_trip_details(int(tid))
                except:
                    print("Invalid ID.")
        elif choice == '6':
            generate_random_delay()
        elif choice == '7':
            update_incident_workflow()
        elif choice == '8':
            list_incidents()
        elif choice == '9':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-9.")

if __name__ == "__main__":
    main()