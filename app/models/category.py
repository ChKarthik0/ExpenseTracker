from app import db
from flask_login import UserMixin

class Category(UserMixin, db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False, default="expense")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    transactions = db.relationship('Transaction', back_populates='category', cascade='all, delete')
    expenses = db.relationship('Expense', back_populates='category', cascade='all, delete-orphan')
    