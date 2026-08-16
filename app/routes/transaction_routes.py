from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.models import db, Expense, Income

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        pass
    return render_template('add_expense.html')

@transaction_bp.route('/add-income', methods=['GET', 'POST'])
@login_required
def add_income():
    if request.method == 'POST':
        # Save income
        pass
    return render_template('add_income.html')

@transaction_bp.route('/transactions')
@login_required
def all_transactions():
    # Show table of transactions
    return render_template('transactions.html')
