from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, Blueprint
from app.forms import ExpenseForm
from app.models.category import Category
from app.models.expense import Expense
from sqlalchemy import or_
from app import db

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()

    # ✅ Fetch both default categories (user_id NULL) + user-specific categories
    categories = Category.query.filter(
        or_(Category.user_id == current_user.id, Category.user_id.is_(None))
    ).order_by(Category.name.asc()).all()

    # ✅ Dynamically populate dropdown
    form.category.choices = [(cat.id, cat.name) for cat in categories]

    # ✅ Debugging log to confirm categories loaded
    print("DEBUG Categories:", [(cat.id, cat.name, cat.user_id) for cat in categories])

    if form.validate_on_submit():
        new_expense = Expense(
            amount=form.amount.data,
            date=form.date.data,
            category_id=form.category.data,
            description=form.description.data,
            payment_method=form.payment_method.data,
            recurring=form.recurring.data,
            tags=form.tags.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()
        flash('✅ Expense added successfully!', 'success')
        return redirect(url_for('dashboard.dashboard_home'))

    return render_template('add_expense.html', form=form)
