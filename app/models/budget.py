from app import db
from datetime import datetime
from flask_login import UserMixin


class Budget(UserMixin,db.Model):
     __tablename__ = 'budget'
     id = db.Column(db.Integer, primary_key=True)
     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
     category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
     amount = db.Column(db.Numeric, nullable=False)
     month = db.Column(db.String(7), nullable=False)  # Format: 'YYYY-MM'
     created_at = db.Column(db.DateTime, default=datetime.utcnow)

     user = db.relationship('User', backref=db.backref('budgets', lazy=True))
     category = db.relationship('Category', backref=db.backref('budgets', lazy=True))