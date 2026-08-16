from sqlalchemy import Column, Integer, Numeric, Date, Text, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app import db 
from flask_login import UserMixin

class Expense(UserMixin,db.Model):
    __tablename__ = 'expense'

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    description = Column(Text)
    date = Column(Date, nullable=False)
    payment_method = Column(String(50))
    recurring = Column(Boolean, default=False)
    tags = Column(Text)
    notes = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

    # Relationships
    category = relationship('Category', back_populates='expenses')
    user = relationship('User', back_populates='expenses')