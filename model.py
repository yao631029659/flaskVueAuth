from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Customers(db.Model):
    customerId=db.Column(db.Integer,primary_key=True)
    companyName=db.Column(db.String(255))
    contactName=db.Column(db.String(255))
    phone=db.Column(db.String(255))

    def __init__(self,companyName,contactName,phone):
        self.companyName=companyName
        self.contactName=contactName
        self.phone=phone


