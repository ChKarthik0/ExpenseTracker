from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    expenses = db.relationship('Expense', back_populates='user', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', cascade='all, delete-orphan')
    