# models.py

from flask_login import UserMixin
from .. import db
from datetime import datetime
import pytz

UTC = pytz.utc
ASP = pytz.timezone('america/sao_paulo')
datetime_ist = datetime.now(ASP)


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    database_accesses = db.relationship(
        'Database_access', backref='user', lazy=True)


class Database_access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    db_user = db.Column(db.String(100), nullable=False)
    db_password = db.Column(db.String(100), nullable=False)
    db_name = db.Column(db.String(1000), nullable=False)
    db_host = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime_ist, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime_ist,
                           onupdate=datetime_ist, nullable=False)
