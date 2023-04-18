from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    trans_type = db.Column(db.Integer)
    trans_date = db.Column(db.Date)
    trans_sum =db.Column(db.Double)
    trans_partener=db.Column(db.String(200))
    trans_status = db.Column(db.String(200), default = 'Pending')

class Partener(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    partener_name = db.Column(db.String(200))
    balance_0 =db.Column(db.Double)
    balance_130 =db.Column(db.Double)
    balance_3160 =db.Column(db.Double)
    balance_60 =db.Column(db.Double)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Sold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sold_banca = db.Column(db.Double)
