from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    fio = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=0)
    admin = db.Column(db.Integer, default=0)

    events = db.relationship('Events', backref='Users', lazy='dynamic')
    event_users = db.relationship('Event_users', backref='Users', lazy='dynamic')

    @property
    def dictor(self):
        return {"ID": self.id,
                "login": self.login,
                "password": self.password,
                "FIO": self.fio,
                "age": self.age,
                "balance": self.balance,
                "admin": self.admin
                }


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    adress = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    start_datetime = db.Column(db.Integer, nullable=False)
    end_datetime = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String)
    organizer = db.Column(db.Integer, db.ForeignKey('users.id'))


class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_event = db.Column(db.Integer, db.ForeignKey('events.id'))
    type = db.Column(db.Integer, db.ForeignKey('types.id'))
    #on = db.Column(db.Boolean)


class Types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    #ticket_count = db.Column(db.Integer)
    id_event = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)


class Discounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discount = db.Column(db.String, nullable=False)


class Event_users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_event = db.Column(db.Integer, db.ForeignKey('events.id'))
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
