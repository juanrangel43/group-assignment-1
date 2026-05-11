# models.py
#
# This file is where you define your ORM models. Models represent tables in the database,
# and each instance of a model corresponds to a row in that table.
#
# Models should inherit from the `Base` class, which provides methods for interacting with the database,
# such as saving records, querying, and deleting.
#
# In this file, you will:
#   - Define your own models, from your database schema in this project, by subclassing the `Base` class.
#   - Use `Column` objects to define columns and their types (e.g., `Integer`, `String`).
#   - Add attributes to each model class to represent columns in the corresponding database table.
#   - Define additional methods in the models as necessary for specific functionality (e.g., custom queries,
#     business logic, etc.).
#
#
# Students should implement their own models, specifying the columns using `Column` and selecting the appropriate
# `types` for each column, such as `Integer`, `String`, `Boolean`, etc.
#


from api.columns import Column
from api.datatypes import Integer, String, Boolean, Float, Date, DateTime, Timestamp, Decimal
from api.base import Base
from api.relations import Relation

class User(Base):
    __name__ = "User"
    user_id = Column(Integer, primary_key=True, auto_increment=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    def __repr__(self):
        return f"User(user_id={self.user_id}, username='{self.username}')"

class Admin(Base):
    __name__ = "Admin"
    admin_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False, unique=True)
    role_name = Column(String, nullable=False)
    access_level = Column(String, nullable=False)
    admin_status = Column(String, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="admin")
    def __repr__(self):
        return f"Admin(admin_id={self.admin_id}, user_id={self.user_id})"

class Employee(Base):
    __name__ = "Employee"
    employee_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False, unique=True)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False)
    job_title = Column(String, nullable=False)
    employment_status = Column(String, nullable=False)
    hire_date = Column(Date, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="employee")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="employees")
    def __repr__(self):
        return f"Employee(employee_id={self.employee_id}, user_id={self.user_id})"

class Officer(Base):
    __name__ = "Officer"
    officer_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False, unique=True)
    badge_number = Column(String, nullable=False, unique=True)
    rank = Column(String, nullable=False)
    assigned_shift = Column(String, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="officer")
    def __repr__(self):
        return f"Officer(officer_id={self.officer_id}, badge_number='{self.badge_number}')"

class Agency(Base):
    __name__ = "Agency"
    agency_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False, unique=True)
    contact_phone = Column(String, nullable=False)
    hq_street = Column(String, nullable=False)
    hq_city = Column(String, nullable=False)
    hq_state = Column(String, nullable=False)
    hq_zip = Column(String, nullable=False)
    def __repr__(self):
        return f"Agency(agency_id={self.agency_id}, name='{self.name}')"

class Station(Base):
    __name__ = "Station"
    station_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    zone_code = Column(String, nullable=False)
    def __repr__(self):
        return f"Station(station_id={self.station_id}, name='{self.name}')"

class Mode(Base):
    __name__ = "Mode"
    mode_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    typical_use_case = Column(String, nullable=False)
    def __repr__(self):
        return f"Mode(mode_id={self.mode_id}, name='{self.name}')"

class Report_Category(Base):
    __name__ = "Report_Category"
    category_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    escalation_flag = Column(Boolean, nullable=False)
    def __repr__(self):
        return f"Report_Category(category_id={self.category_id}, name='{self.name}')"

class Incident_Status(Base):
    __name__ = "Incident_Status"
    status_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    display_order = Column(Integer, nullable=False)
    def __repr__(self):
        return f"Incident_Status(status_id={self.status_id}, name='{self.name}')"

class Vehicle_Status(Base):
    __name__ = "Vehicle_Status"
    status_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    operational_flag = Column(String, nullable=False)
    def __repr__(self):
        return f"Vehicle_Status(status_id={self.status_id}, name='{self.name}')"

class Hazards(Base):
    __name__ = "Hazards"
    hazards_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    severity_class = Column(String, nullable=False)
    def __repr__(self):
        return f"Hazards(hazards_id={self.hazards_id}, name='{self.name}')"

class Priority_Level(Base):
    __name__ = "Priority_Level"
    priority_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity_rank = Column(Integer, nullable=False)
    def __repr__(self):
        return f"Priority_Level(priority_id={self.priority_id}, name='{self.name}')"

class Responder(Base):
    __name__ = "Responder"
    responder_id = Column(Integer, primary_key=True, auto_increment=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    responder_category = Column(String, nullable=False)
    def __repr__(self):
        return f"Responder(responder_id={self.responder_id}, name='{self.name}')"

class Line(Base):
    __name__ = "Line"
    line_id = Column(Integer, primary_key=True, auto_increment=True)
    agency_id = Column(Integer, foreign_key="Agency(agency_id)", nullable=False)
    mode_id = Column(Integer, foreign_key="Mode(mode_id)", nullable=False)
    name = Column(String, nullable=False, unique=True)
    line_color = Column(String, nullable=False)
    service_pattern = Column(String, nullable=False)
    agency = Relation(model_name="Agency", foreign_key="agency_id", backreference="lines")
    mode = Relation(model_name="Mode", foreign_key="mode_id", backreference="lines")
    def __repr__(self):
        return f"Line(line_id={self.line_id}, name='{self.name}')"

class Data_Feed(Base):
    __name__ = "Data_Feed"
    feed_Id = Column(Integer, primary_key=True, auto_increment=True)
    feed_name = Column(String, nullable=False, unique=True)
    feed_type = Column(String, nullable=False)
    def __repr__(self):
        return f"Data_Feed(feed_Id={self.feed_Id}, feed_name='{self.feed_name}')"

class Station_Agency(Base):
    __name__ = "Station_Agency"
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False, primary_key=True)
    agency_id = Column(Integer, foreign_key="Agency(agency_id)", nullable=False, primary_key=True)
    service_start_date = Column(Date, nullable=False)
    service_end_date = Column(Date, nullable=True)
    service_notes = Column(String, nullable=True)
    station = Relation(model_name="Station", foreign_key="station_id", backreference="station_agencies")
    agency = Relation(model_name="Agency", foreign_key="agency_id", backreference="station_agencies")
    def __repr__(self):
        return f"Station_Agency(station_id={self.station_id}, agency_id={self.agency_id})"

class Line_Station(Base):
    __name__ = "Line_Station"
    line_id = Column(Integer, foreign_key="Line(line_id)", nullable=False, primary_key=True)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False, primary_key=True)
    sequence_number = Column(Integer, nullable=False)
    platform_info = Column(String, nullable=True)
    destination_label = Column(String, nullable=False)
    line = Relation(model_name="Line", foreign_key="line_id", backreference="line_stations")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="line_stations")
    def __repr__(self):
        return f"Line_Station(line_id={self.line_id}, station_id={self.station_id}, seq={self.sequence_number})"

class Weather(Base):
    __name__ = "Weather"
    weather_id = Column(Integer, primary_key=True, auto_increment=True)
    feed_id = Column(Integer, foreign_key="Data_Feed(feed_Id)", nullable=False)
    status = Column(String, nullable=False)
    temperature = Column(Decimal, nullable=False)
    recorded_timestamp = Column(Timestamp, nullable=False)
    data_feed = Relation(model_name="Data_Feed", foreign_key="feed_id", backreference="weather_records")
    def __repr__(self):
        return f"Weather(weather_id={self.weather_id}, status='{self.status}')"

class Incident_Report(Base):
    __name__ = "Incident_Report"
    incident_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    status_id = Column(Integer, foreign_key="Incident_Status(status_id)", nullable=True)
    category_id = Column(Integer, foreign_key="Report_Category(category_id)", nullable=False)
    weather_id = Column(Integer, foreign_key="Weather(weather_id)", nullable=False)
    priority_id = Column(Integer, foreign_key="Priority_Level(priority_id)", nullable=False)
    description = Column(String, nullable=False)
    reported_timestamp = Column(Timestamp, nullable=False)
    incident_source = Column(String, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="incidents")
    status = Relation(model_name="Incident_Status", foreign_key="status_id", backreference="incidents")
    category = Relation(model_name="Report_Category", foreign_key="category_id", backreference="incidents")
    weather = Relation(model_name="Weather", foreign_key="weather_id", backreference="incidents")
    priority = Relation(model_name="Priority_Level", foreign_key="priority_id", backreference="incidents")
    def __repr__(self):
        return f"Incident_Report(incident_id={self.incident_id}, user_id={self.user_id})"

class Incident_Station(Base):
    __name__ = "Incident_Station"
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False, primary_key=True)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False, primary_key=True)
    location_note = Column(String, nullable=False)
    area_type = Column(String, nullable=False)
    linked_timestamp = Column(Timestamp, nullable=False)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="incident_stations")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="incident_stations")
    def __repr__(self):
        return f"Incident_Station(incident_id={self.incident_id}, station_id={self.station_id})"

class Incident_Train(Base):
    __name__ = "Incident_Train"
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False, primary_key=True)
    train_id = Column(Integer, foreign_key="Train(train_id)", nullable=False, primary_key=True)
    train_section_note = Column(String, nullable=False)
    impact_type = Column(String, nullable=False)
    linked_timestamp = Column(Timestamp, nullable=False)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="incident_trains")
    train = Relation(model_name="Train", foreign_key="train_id", backreference="incident_trains")
    def __repr__(self):
        return f"Incident_Train(incident_id={self.incident_id}, train_id={self.train_id})"

class Incident_Photo(Base):
    __name__ = "Incident_Photo"
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False, primary_key=True)
    photo_sequence = Column(Integer, nullable=False, primary_key=True)
    photo_url = Column(String, nullable=False)
    captured_timestamp = Column(Timestamp, nullable=False)
    caption = Column(String, nullable=True)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="photos")
    def __repr__(self):
        return f"Incident_Photo(incident_id={self.incident_id}, seq={self.photo_sequence})"

class Incident_History(Base):
    __name__ = "Incident_History"
    history_id = Column(Integer, primary_key=True, auto_increment=True)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False)
    timestamp = Column(DateTime, nullable=False)
    action_desc = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="history")
    def __repr__(self):
        return f"Incident_History(history_id={self.history_id}, incident_id={self.incident_id})"

class Incident_Hazard(Base):
    __name__ = "Incident_Hazard"
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False, primary_key=True)
    hazard_id = Column(Integer, foreign_key="Hazards(hazards_id)", nullable=False, primary_key=True)
    hazard_severity = Column(String, nullable=False)
    detected_timestamp = Column(Timestamp, nullable=False)
    mitigation_status = Column(String, nullable=False)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="incident_hazards")
    hazard = Relation(model_name="Hazards", foreign_key="hazard_id", backreference="incident_hazards")
    def __repr__(self):
        return f"Incident_Hazard(incident_id={self.incident_id}, hazard_id={self.hazard_id})"

class Car(Base):
    __name__ = "Car"
    car_id = Column(Integer, primary_key=True, auto_increment=True)
    agency_id = Column(Integer, foreign_key="Agency(agency_id)", nullable=False)
    status_id = Column(Integer, foreign_key="Vehicle_Status(status_id)", nullable=False)
    car_name = Column(String, nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    car_type = Column(String, nullable=False)
    agency = Relation(model_name="Agency", foreign_key="agency_id", backreference="cars")
    status = Relation(model_name="Vehicle_Status", foreign_key="status_id", backreference="cars")
    def __repr__(self):
        return f"Car(car_id={self.car_id}, car_name='{self.car_name}')"

class Train(Base):
    __name__ = "Train"
    train_id = Column(Integer, primary_key=True, auto_increment=True)
    agency_id = Column(Integer, foreign_key="Agency(agency_id)", nullable=False)
    status_id = Column(Integer, foreign_key="Vehicle_Status(status_id)", nullable=False)
    train_code = Column(String, nullable=False, unique=True)
    capacity_total = Column(Integer, nullable=False)
    service_type = Column(String, nullable=False)
    agency = Relation(model_name="Agency", foreign_key="agency_id", backreference="trains")
    status = Relation(model_name="Vehicle_Status", foreign_key="status_id", backreference="trains")
    def __repr__(self):
        return f"Train(train_id={self.train_id}, train_code='{self.train_code}')"

class Train_Car(Base):
    __name__ = "Train_Car"
    train_id = Column(Integer, foreign_key="Train(train_id)", nullable=False, primary_key=True)
    car_id = Column(Integer, foreign_key="Car(car_id)", nullable=False, primary_key=True)
    car_order = Column(Integer, nullable=False)
    coupled_timestamp = Column(Timestamp, nullable=False)
    car_role = Column(String, nullable=False)
    train = Relation(model_name="Train", foreign_key="train_id", backreference="train_cars")
    car = Relation(model_name="Car", foreign_key="car_id", backreference="train_cars")
    def __repr__(self):
        return f"Train_Car(train_id={self.train_id}, car_id={self.car_id})"

class Trip(Base):
    __name__ = "Trip"
    trip_id = Column(Integer, primary_key=True, auto_increment=True)
    train_id = Column(Integer, foreign_key="Train(train_id)", nullable=False)
    line_id = Column(Integer, foreign_key="Line(line_id)", nullable=False)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    trip_status = Column(String, nullable=False)
    train = Relation(model_name="Train", foreign_key="train_id", backreference="trips")
    line = Relation(model_name="Line", foreign_key="line_id", backreference="trips")
    def __repr__(self):
        return f"Trip(trip_id={self.trip_id}, train_id={self.train_id})"

class Stop(Base):
    __name__ = "Stop"
    stop_id = Column(Integer, primary_key=True, auto_increment=True)
    trip_id = Column(Integer, foreign_key="Trip(trip_id)", nullable=False)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False)
    scheduled_arrival = Column(DateTime, nullable=False)
    scheduled_departure = Column(DateTime, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    trip = Relation(model_name="Trip", foreign_key="trip_id", backreference="stops")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="stops")
    def __repr__(self):
        return f"Stop(stop_id={self.stop_id}, trip_id={self.trip_id}, seq={self.sequence_number})"

class Live_Feed(Base):
    __name__ = "Live_Feed"
    feed_id = Column(Integer, primary_key=True, auto_increment=True)
    stop_id = Column(Integer, foreign_key="Stop(stop_id)", nullable=False)
    update_timestamp = Column(DateTime, nullable=False)
    estimated_arrival_time = Column(DateTime, nullable=False)
    capacity_percentage = Column(Integer, nullable=False)
    stop = Relation(model_name="Stop", foreign_key="stop_id", backreference="live_feeds")
    def __repr__(self):
        return f"Live_Feed(feed_id={self.feed_id}, stop_id={self.stop_id})"

class Delay_Propagation(Base):
    __name__ = "Delay_Propagation"
    propagation_id = Column(Integer, primary_key=True, auto_increment=True)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False)
    trip_id = Column(Integer, foreign_key="Trip(trip_id)", nullable=False)
    stop_id = Column(Integer, foreign_key="Stop(stop_id)", nullable=False)
    delay_minutes = Column(Integer, nullable=False)
    calculated_timestamp = Column(Timestamp, nullable=False)
    impact_scope = Column(String, nullable=False)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="delay_propagations")
    trip = Relation(model_name="Trip", foreign_key="trip_id", backreference="delay_propagations")
    stop = Relation(model_name="Stop", foreign_key="stop_id", backreference="delay_propagations")
    def __repr__(self):
        return f"Delay_Propagation(propagation_id={self.propagation_id}, incident_id={self.incident_id})"

class Saved_Station(Base):
    __name__ = "Saved_Station"
    saved_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False)
    created_timestamp = Column(Timestamp, nullable=False)
    custom_label = Column(String, nullable=True)
    notification_enabled = Column(Boolean, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="saved_stations")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="saved_by_users")
    def __repr__(self):
        return f"Saved_Station(saved_id={self.saved_id}, user_id={self.user_id})"

class Upvote(Base):
    __name__ = "Upvote"
    upvote_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False)
    created_timestamp = Column(Timestamp, nullable=False)
    vote_source = Column(String, nullable=True)
    active_flag = Column(Boolean, nullable=True)
    user = Relation(model_name="User", foreign_key="user_id", backreference="upvotes")
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="upvotes")
    def __repr__(self):
        return f"Upvote(upvote_id={self.upvote_id}, user_id={self.user_id})"

class Incident_Update(Base):
    __name__ = "Incident_Update"
    update_id = Column(Integer, primary_key=True, auto_increment=True)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    comment_text = Column(String, nullable=False)
    created_timestamp = Column(Timestamp, nullable=False)
    visibility_status = Column(String, nullable=False)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="updates")
    user = Relation(model_name="User", foreign_key="user_id", backreference="incident_updates")
    def __repr__(self):
        return f"Incident_Update(update_id={self.update_id}, incident_id={self.incident_id})"

class Vote(Base):
    __name__ = "Vote"
    vote_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    update_id = Column(Integer, foreign_key="Incident_Update(update_id)", nullable=False)
    vote_type = Column(String, nullable=False)
    created_timestamp = Column(Timestamp, nullable=False)
    active_flag = Column(Boolean, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="votes")
    update = Relation(model_name="Incident_Update", foreign_key="update_id", backreference="votes")
    def __repr__(self):
        return f"Vote(vote_id={self.vote_id}, user_id={self.user_id})"

class Notification_Preference(Base):
    __name__ = "Notification_Preference"
    preference_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    notification_type = Column(String, nullable=False)
    enabled_flag = Column(Boolean, nullable=False)
    delivery_channel = Column(String, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="notification_preferences")
    def __repr__(self):
        return f"Notification_Preference(preference_id={self.preference_id}, user_id={self.user_id})"

class Notification(Base):
    __name__ = "Notification"
    notification_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=True)
    line_id = Column(Integer, foreign_key="Line(line_id)", nullable=True)
    created_timestamp = Column(Timestamp, nullable=False)
    delivery_status = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    user = Relation(model_name="User", foreign_key="user_id", backreference="notifications")
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="notifications")
    line = Relation(model_name="Line", foreign_key="line_id", backreference="notifications")
    def __repr__(self):
        return f"Notification(notification_id={self.notification_id}, user_id={self.user_id})"

class Dispatch_Low_Level(Base):
    __name__ = "Dispatch_Low_Level"
    low_level_dispatch_id = Column(Integer, primary_key=True, auto_increment=True)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False)
    employee_id = Column(Integer, foreign_key="Employee(employee_id)", nullable=True)
    officer_id = Column(Integer, foreign_key="Officer(officer_id)", nullable=True)
    dispatched_timestamp = Column(Timestamp, nullable=False)
    dispatch_status = Column(String, nullable=False)
    response_notes = Column(String, nullable=True)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="low_level_dispatches")
    employee = Relation(model_name="Employee", foreign_key="employee_id", backreference="low_level_dispatches")
    officer = Relation(model_name="Officer", foreign_key="officer_id", backreference="low_level_dispatches")
    def __repr__(self):
        return f"Dispatch_Low_Level(dispatch_id={self.low_level_dispatch_id}, incident_id={self.incident_id})"

class Dispatch_High_Level(Base):
    __name__ = "Dispatch_High_Level"
    high_level_dispatch_id = Column(Integer, primary_key=True, auto_increment=True)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False)
    responder_id = Column(Integer, foreign_key="Responder(responder_id)", nullable=False)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False)
    dispatched_timestamp = Column(Timestamp, nullable=False)
    dispatch_status = Column(String, nullable=False)
    priority_note = Column(String, nullable=True)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="high_level_dispatches")
    responder = Relation(model_name="Responder", foreign_key="responder_id", backreference="high_level_dispatches")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="high_level_dispatches")
    def __repr__(self):
        return f"Dispatch_High_Level(dispatch_id={self.high_level_dispatch_id}, incident_id={self.incident_id})"

class Fare_Log(Base):
    __name__ = "Fare_Log"
    log_id = Column(Integer, primary_key=True, auto_increment=True)
    incident_id = Column(Integer, foreign_key="Incident_Report(incident_id)", nullable=False)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False)
    detected_timestamp = Column(Timestamp, nullable=False)
    fare_amount = Column(Decimal, nullable=False)
    detection_method = Column(String, nullable=False)
    incident = Relation(model_name="Incident_Report", foreign_key="incident_id", backreference="fare_logs")
    user = Relation(model_name="User", foreign_key="user_id", backreference="fare_logs")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="fare_logs")
    def __repr__(self):
        return f"Fare_Log(log_id={self.log_id}, user_id={self.user_id})"

class Distance(Base):
    __name__ = "Distance"
    distance_id = Column(Integer, primary_key=True, auto_increment=True)
    user_id = Column(Integer, foreign_key="User(user_id)", nullable=False)
    station_id = Column(Integer, foreign_key="Station(station_id)", nullable=False)
    miles = Column(Decimal, nullable=False)
    calculated_timestamp = Column(Timestamp, nullable=False)
    calculation_method = Column(String, nullable=True)
    user = Relation(model_name="User", foreign_key="user_id", backreference="distances")
    station = Relation(model_name="Station", foreign_key="station_id", backreference="distances")
    def __repr__(self):
        return f"Distance(distance_id={self.distance_id}, user_id={self.user_id}, station_id={self.station_id})"