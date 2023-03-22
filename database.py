from flask_sqlalchemy import SQLAlchemy
from flask import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    phone = db.Column(db.Text)
    psw = db.Column(db.Text)
    user_type = db.Column(db.Text)
    user_id = db.Column(db.Text)
    profilepic = db.Column(db.Text)
    loc = db.Column(db.Text)
    fprint = db.Column(db.Text)
    pin = db.Column(db.Text)
    name = db.Column(db.Text)

class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    account_balance = db.Column(db.Text)
    account_id = db.Column(db.Text)
    account_number = db.Column(db.Text)
    user_id = db.Column(db.Text)
    account_name = db.Column(db.Text)

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.Text)
    recipient = db.Column(db.Text)
    amount = db.Column(db.Text)
    timeline = db.Column(db.Text)
    remark = db.Column(db.Text)

class Withdrawals(db.Column):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Text)
    account_id = db.Column(db.Text)
    timeline = db.Column(db.Text)
    amount = db.Column(db.Text)

class Depositions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Text)
    account_id = db.Column(db.Text)
    timeline = db.Column(db.Text)
    amount = db.Column(db.Text)

class Database(object):
    
    @staticmethod
    def insert_into_table(table, data):
        signature = table(**data)
        db.session.add(signature)
        db.session.commit()
    
    @staticmethod
    def remove_from_table(table, keys):
        data = table.query.filter_by(**keys).first()
        db.session.delete(data)
        db.session.commit()

    @staticmethod
    def update_table(table, keys, updates):
        row = table.query.filter_by(**keys)
        row.update(updates)
        db.session.commit()

    @staticmethod
    def find_one_from_table(table, keys):
        data = table.query.filter_by(**keys).first()
        return data

    @staticmethod
    def find_many_from_table(table, keys):
        if keys != {}:
            rows = table.query.filter_by(**keys)
        else:
            rows = table.query.all()
        return [row for row in rows]