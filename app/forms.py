from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    phone = StringField('Phone Number', validators=[DataRequired(), Regexp(r'^\+?\d{10,15}$', message="Enter a valid phone number")])
    email = StringField('Email', validators=[ DataRequired(),Email(message="Enter a valid email address."), Length(max=120) ])
    password = PasswordField('Password', validators=[ DataRequired(), Length(min=6, message="Password must be at least 6 characters.") ])
    confirm_password = PasswordField('Confirm Password', validators=[ DataRequired(), EqualTo('password', message="Passwords must match.") ])
    agree_terms = BooleanField('I agree to the Terms and Conditions', validators=[ DataRequired(message="You must agree to the terms.") ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[ DataRequired(), Email(message="Enter a valid email address."), Length(max=120) ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])  # ✅ changed from name → username
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")
    
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, TextAreaField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AddExpenseForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('UPI', 'UPI'), ('Card', 'Card'), ('Cash', 'Cash')
    ], validators=[DataRequired()])
    recurring = SelectField('Recurring', choices=[
        ('No', 'No'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')
    ], validators=[DataRequired()])
    tags = StringField('Tags')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Expense')

    
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, DateField, SubmitField
from wtforms.validators import DataRequired

class AddIncomeForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    description = StringField('Description')
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Save')