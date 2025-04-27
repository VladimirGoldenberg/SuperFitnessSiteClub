from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    session_length = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Registration {self.student_name} - {self.day_of_week} {self.time}>'

class RegistrationManager:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        db.init_app(app)

    def add_registration(self, student_name, student_email, day_of_week, time, session_length):
        # Check if the student is already registered for this slot
        existing_registration = Registration.query.filter_by(
            student_email=student_email,
            day_of_week=day_of_week,
            time=time
        ).first()

        if existing_registration:
            return False  # Already registered

        # Count how many people are already registered for this slot
        registrations_count = Registration.query.filter_by(
            day_of_week=day_of_week,
            time=time
        ).count()

        if registrations_count >= 3:
            return False  # Slot is full

        # Add the new registration
        new_registration = Registration(
            student_name=student_name,
            student_email=student_email,
            day_of_week=day_of_week,
            time=time,
            session_length=session_length
        )
        db.session.add(new_registration)
        db.session.commit()
        return True

def create_tables(app):
    with app.app_context():
        db.create_all()
