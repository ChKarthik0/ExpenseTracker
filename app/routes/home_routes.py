from flask import Blueprint, render_template
from flask_login import current_user

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    # No redirect needed, let base.html decide what to show
    return render_template('index.html')
