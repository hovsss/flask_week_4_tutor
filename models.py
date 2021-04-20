from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

teachers_goals_association = db.Table('teachers_goals',
                                      db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
                                      db.Column('goal_id', db.Integer, db.ForeignKey('goals.id'))
                                      )


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    about = db.Column(db.Text)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(100))
    price = db.Column(db.Integer, nullable=False)
    free = db.Column(db.UnicodeText, nullable=False)
    booking = db.relationship("Booking", back_populates='teacher')
    goals = db.relationship("Goal", secondary=teachers_goals_association, back_populates="teachers")


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(14), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    weekday = db.Column(db.String(10))
    time = db.Column(db.String(10))
    teacher = db.relationship("Teacher", back_populates="booking")


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.String(100))
    time = db.Column(db.String(100))


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    goal = db.Column(db.String(100), nullable=False)
    teachers = db.relationship("Teacher", secondary=teachers_goals_association, back_populates="goals")
