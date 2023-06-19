# models.py

from flask_login import UserMixin
from .. import db
from datetime import datetime
import pytz

ASP = pytz.timezone('america/sao_paulo')
datetime_ist = datetime.now(ASP)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    Database_accesses = db.relationship(
        'Database_access', backref='user', lazy=True)
    Training_frequency = db.relationship(
        'Training_frequency', backref='user', lazy=True)
    Transactions = db.relationship('Transactions', backref='user', lazy=True)
    User_api = db.relationship('User_api', backref='user', lazy=True)
    Training_status = db.relationship(
        'Training_status', backref='user', lazy=True)
    Items = db.relationship(
        'Items', backref='user', lazy=True)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name


class Database_access(db.Model):
    __tablename__ = 'database_access'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    db_user = db.Column(db.String(100), nullable=False)
    db_password = db.Column(db.String(100), nullable=False)
    db_name = db.Column(db.String(1000), nullable=False)
    db_host = db.Column(db.String(100), nullable=False)
    db_view = db.Column(db.String(100), nullable=False)
    db_sgbd = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime_ist, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime_ist,
                           onupdate=datetime_ist, nullable=False)

    def __init__(self, user_id, db_user, db_password, db_name, db_host, db_view, db_sgbd):
        self.user_id = user_id
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.db_host = db_host
        self.db_view = db_view
        self.db_sgbd = db_sgbd


class Training_frequency(db.Model):
    __tablename__ = 'training_frequency'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tr_activated = db.Column(db.Integer, default=0, nullable=False)
    tr_frequency = db.Column(db.Enum('daily', 'weekly', 'fortnightly', 'monthly', name='train_freq'),
                             default='monthly', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime_ist, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime_ist,
                           onupdate=datetime_ist, nullable=False)

    def __init__(self, user_id, tr_activated, tr_frequency):
        self.user_id = user_id
        self.tr_activated = tr_activated
        self.tr_frequency = tr_frequency


class Transactions(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    id_transaction = db.Column(db.Integer, nullable=False)
    id_item = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name_item = db.Column(db.String(150), nullable=False)
    data_transaction = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime_ist, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime_ist,
                           onupdate=datetime_ist, nullable=False)

    def __init__(self, id_transaction, id_item, customer_id, user_id, name_item, data_transaction, created_at):
        self.id_transaction = id_transaction
        self.id_item = id_item
        self.customer_id = customer_id
        self.user_id = user_id
        self.name_item = name_item
        self.data_transaction = data_transaction
        self.created_at = created_at


class Items(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    id_item = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name_item = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime_ist, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime_ist,
                           onupdate=datetime_ist, nullable=False)

    def __init__(self, id_item, customer_id, user_id, name_item, created_at):
        self.id_item = id_item
        self.customer_id = customer_id
        self.user_id = user_id
        self.name_item = name_item
        self.created_at = created_at


class User_api(db.Model):
    __tablename__ = 'user_api'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False)
    hash = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime_ist, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime_ist,
                           onupdate=datetime_ist, nullable=False)

    def __init__(self, username, hash, user_id):
        self.username = username
        self.hash = hash
        self.user_id = user_id


class Training_status(db.Model):
    __tablename__ = 'training_status'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    message = db.Column(db.String(200))

    def __init__(self, user_id, start, status):
        self.user_id = user_id
        self.start = start
        self.end = None
        self.status = status
        self.message = None
