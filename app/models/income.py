from app import db
from flask_login import UserMixin

class Income(UserMixin,db.Model):
    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text) 
    date = db.Column(db.Date, nullable=False)
    recurring = db.Column(db.String, default='No') 
    payment_method = db.Column(db.String(50)) 
    notes = db.Column(db.Text)  