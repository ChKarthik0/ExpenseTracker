from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, make_response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import MultiDict
from app.models import Transaction, Category
from app.models.user import User
from app.forms import ProfileForm, PasswordChangeForm
from app.models import Budget, Income, Expense, Transaction
from datetime import datetime, date, timedelta
from sqlalchemy import extract, func
import io, os, csv
from app import db 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, DecimalField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from flask_wtf.file import FileAllowed
from decimal import Decimal
from app.forms import AddExpenseForm, AddIncomeForm
from xhtml2pdf import pisa
from flask import render_template_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard_home():
    user_id = current_user.id
    today = date.today()
    now = datetime.now()
    current_month = today.strftime("%Y-%m")

    # Monthly Income
    monthly_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == user_id,
        extract('month', Income.date) == now.month,
        extract('year', Income.date) == now.year
    ).scalar() or 0

    # Monthly Expenses
    monthly_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        extract('month', Transaction.date) == now.month,
        extract('year', Transaction.date) == now.year
    ).scalar() or 0
    monthly_expenses = abs(monthly_expenses)

    # Today's Expenses
    today_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date == today
    ).scalar() or 0
    today_expenses = abs(today_expenses)

    # Today's transaction count (expenses only)
    today_transaction_count = db.session.query(func.count()).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date == today
    ).scalar() or 0

    # Recent Incomes, Expenses, and All Transactions
    recent_incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.amount < 0
    ).order_by(Transaction.date.desc()).limit(5).all()
    recent_transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).limit(5).all()

    # Get current month budgets and transactions
    budgets = Budget.query.filter_by(user_id=user_id, month=current_month).all()
    transactions = Transaction.query.filter_by(user_id=user_id).filter(
        extract('month', Transaction.date) == now.month,
        extract('year', Transaction.date) == now.year
    ).all()

    # Calculate spent per category ID
    category_spent = {}
    for txn in transactions:
        if txn.type == 'expense' and txn.category_id:
            category_spent[txn.category_id] = category_spent.get(txn.category_id, 0) + abs(float(txn.amount))

    # Calculate budget usage safely
    total_budget = sum(float(b.amount) for b in budgets)
    total_spent = Decimal("0.0")

    # Default values to avoid UnboundLocalError
    budget_usage = 0.0  

    for b in budgets:
        spent = Decimal(str(category_spent.get(b.category_id, 0)))
        b.spent = spent
        b.usage_percent = round((spent / b.amount) * 100, 2) if b.amount > 0 else 0
        total_spent += spent

    # ✅ Now calculate budget_usage AFTER total_spent is ready
    if total_budget > 0:
        budget_usage = round((total_spent / Decimal(total_budget)) * 100, 1)

    # Budget usage levels
    on_track_count = sum(1 for b in budgets if b.usage_percent < 80)
    close_to_limit_count = sum(1 for b in budgets if 80 <= b.usage_percent < 100)
    over_budget_count = sum(1 for b in budgets if b.usage_percent >= 100)

    # Expense pie chart by category
    expense_query = db.session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction.category).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense'
    ).group_by(Category.name).all()

    expense_labels = [label for label, _ in expense_query]
    expense_values = [abs(value) for _, value in expense_query]

    # Income pie chart by source
    income_query = db.session.query(
        Income.source,
        func.sum(Income.amount)
    ).filter(
        Income.user_id == user_id
    ).group_by(Income.source).all()

    income_labels = [label for label, _ in income_query]
    income_values = [value for _, value in income_query]

    # Budget pie chart
    budget_labels = [b.category.name for b in budgets]
    budget_percentages = [b.usage_percent for b in budgets]

    return render_template(
        'dashboard.html',
        user=current_user,
        today=today,
        now=now,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        today_expenses=today_expenses,
        today_transaction_count=today_transaction_count,
        recent_incomes=recent_incomes,
        recent_expenses=recent_expenses,
        recent_transactions=recent_transactions,
        total_budget=total_budget,
        total_spent=total_spent,
        on_track_count=on_track_count,
        close_to_limit_count=close_to_limit_count,
        over_budget_count=over_budget_count,
        budgets=budgets,
        budget_usage=budget_usage,
        expense_labels=expense_labels,
        expense_values=expense_values,
        income_labels=income_labels,
        income_values=income_values,
        budget_labels=budget_labels,
        budget_percentages=budget_percentages
    )
    
class AddExpenseForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = StringField('Description')
    date = DateField('Date', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer')
    ], validators=[DataRequired()])
    recurring = SelectField('Recurring', choices=[
        ('no', 'No'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], default='no')
    tags = StringField('Tags')
    notes = TextAreaField('Notes')


from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Expense, Category
from datetime import datetime
from sqlalchemy import or_
from app.routes.dashboard_routes import dashboard_bp  # Ensure your Blueprint is imported

@dashboard_bp.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = AddExpenseForm()

    # Populate category dropdown with user-specific categories
    categories = Category.query.filter(
        or_(Category.user_id == current_user.id, Category.user_id.is_(None))).order_by(Category.name.asc()).all()
    form.category.choices = [(cat.id, cat.name) for cat in categories]

    if form.validate_on_submit():
        try:
            # Recurring logic (optional field from form)
            recurring_input = form.recurring.data
            tags = form.tags.data
            notes = form.notes.data

            new_transaction = Transaction(
                user_id=current_user.id,
                type='expense',
                amount=form.amount.data,
                category_id=int(form.category.data),
                description=form.description.data,
                date=form.date.data,
                payment_method=form.payment_method.data,
                tags=tags,
                notes=notes
            )

            db.session.add(new_transaction)
            db.session.commit()

            flash('Expense added successfully!', 'success')
            return redirect(url_for('dashboard.transactions'))  # use correct route
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving expense: {str(e)}', 'danger')

    return render_template('add_expense.html', form=form)

@dashboard_bp.route('/add_income', methods=['GET', 'POST'])
@login_required
def add_income():
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))
            source = request.form.get('source')  # This will be stored as description
            description = request.form.get('description')
            date_str = request.form.get('date')
            payment_method = request.form.get('payment_method')
            recurring = request.form.get('recurring')  # Optional
            notes = request.form.get('notes')
            tags = request.form.get('tags')  # Optional

            # Convert string to date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Save to Income table
            new_income = Income(
                user_id=current_user.id,
                amount=amount,
                source=source,
                description=description,
                date=date_obj,
                payment_method=payment_method,
                recurring=recurring,
                notes=notes
            )
            db.session.add(new_income)

            # Save to Transactions table
            new_transaction = Transaction(
                user_id=current_user.id,
                type='income',
                amount=amount,
                category_id=None,
                description=f"{source} - {description}",
                date=date_obj,
                payment_method=payment_method,
                tags=tags,
                notes=notes
            )
            db.session.add(new_transaction)

            db.session.commit()
            flash('Income added successfully!', 'success')
            return redirect(url_for('dashboard.transactions'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding income: {str(e)}", 'danger')
            return redirect(url_for('dashboard.add_income'))

    return render_template('add_income.html')

    
def apply_filters(transactions_query):
    t_type = request.args.get('type')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')

    if t_type:
        transactions_query = transactions_query.filter_by(type=t_type)
    if category:
        transactions_query = transactions_query.filter(Transaction.category.has(name=category))
    if start_date:
        transactions_query = transactions_query.filter(Transaction.date >= start_date)
    if end_date:
        transactions_query = transactions_query.filter(Transaction.date <= end_date)
    if search:
        transactions_query = transactions_query.filter(Transaction.description.ilike(f"%{search}%"))

    return transactions_query


def apply_sorting(transactions_query):
    sort = request.args.get('sort')
    order = request.args.get('order', 'asc')

    if sort == 'amount':
        transactions_query = transactions_query.order_by(Transaction.amount.asc() if order == 'asc' else Transaction.amount.desc())
    elif sort == 'date':
        transactions_query = transactions_query.order_by(Transaction.date.asc() if order == 'asc' else Transaction.date.desc())
    else:
        transactions_query = transactions_query.order_by(Transaction.date.desc())

    return transactions_query


@dashboard_bp.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    transactions_query = Transaction.query.filter_by(user_id=current_user.id)
    transactions_query = apply_filters(transactions_query)
    transactions_query = apply_sorting(transactions_query)

    pagination = transactions_query.paginate(page=page, per_page=per_page)
    transactions = pagination.items

    # Get all categories for the filter dropdown
    categories = Category.query.with_entities(Category.name).distinct().all()
    category_names = [cat.name for cat in categories]

    return render_template(
    'transactions.html',
    transactions=transactions,
    pagination=pagination,
    categories=category_names,
    selected_type=request.args.get('type', ''),
    selected_category=request.args.get('category', ''),
    selected_start=request.args.get('start_date', ''),
    selected_end=request.args.get('end_date', ''),
    search_query=request.args.get('search', ''),
    current_sort=request.args.get('sort', ''),
    current_order=request.args.get('order', 'asc')
)


@dashboard_bp.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard.transactions'))

    db.session.delete(transaction)
    db.session.commit()
    flash("Transaction deleted successfully.", "success")
    return redirect(url_for('dashboard.transactions'))

@dashboard_bp.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    # Check if transaction belongs to current user
    if transaction.user_id != current_user.id:
        flash("You do not have permission to edit this transaction.", "danger")
        return redirect(url_for('dashboard.transactions'))

    form = AddExpenseForm(obj=transaction) if transaction.type == 'Expense' else AddIncomeForm(obj=transaction)

    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.category = form.category.data
        transaction.description = form.description.data
        transaction.date = form.date.data
        db.session.commit()
        flash("Transaction updated successfully.", "success")
        return redirect(url_for('dashboard.transactions'))

    return render_template('edit_transaction.html', form=form, transaction=transaction)

@dashboard_bp.route("/budget", methods=["GET"])
@login_required
def budget():
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    edit_id = request.args.get("edit_id", type=int)

    budgets = Budget.query.filter_by(user_id=current_user.id, month=current_month).all()
    budget_data = []

    for b in budgets:
        spent = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == b.category_id,
            Transaction.type == "expense",
            extract('year', Transaction.date) == now.year,
            extract('month', Transaction.date) == now.month
        ).scalar() or 0

        spent = Decimal(spent)
        usage = round((spent / b.amount) * 100, 2) if b.amount > 0 else 0
        remaining = round(b.amount - spent, 2)

        budget_data.append({
            "id": b.id,
            "category": b.category,
            "amount": b.amount,
            "spent": spent,
            "remaining": remaining,
            "usage": usage
        })

    categories = Category.query.all()
    total_budget = sum([b["amount"] for b in budget_data])
    total_spent = sum([b["spent"] for b in budget_data])

    return render_template(
        "budget.html",
        budgets=budget_data,
        categories=categories,
        total_budget=total_budget,
        total_spent=total_spent,
        edit_id=edit_id
    )


@dashboard_bp.route("/budget/add", methods=["POST"])
@login_required
def add_budget():
    category_id = request.form["category_id"]
    amount = Decimal(request.form["amount"])
    current_month = datetime.now().strftime('%Y-%m')

    existing = Budget.query.filter_by(user_id=current_user.id, category_id=category_id, month=current_month).first()
    if existing:
        flash("Budget already exists for this category.", "warning")
        return redirect(url_for("dashboard.budget"))

    new_budget = Budget(user_id=current_user.id, category_id=category_id, amount=amount, month=current_month)
    db.session.add(new_budget)
    db.session.commit()
    flash("Budget added successfully.", "success")
    return redirect(url_for("dashboard.budget"))


@dashboard_bp.route("/budget/edit/<int:id>", methods=["POST"])
@login_required
def edit_budget(id):
    budget = Budget.query.get_or_404(id)
    if budget.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard.budget"))

    budget.amount = Decimal(request.form["amount"])
    db.session.commit()
    flash("Budget updated successfully.", "success")
    return redirect(url_for("dashboard.budget"))


@dashboard_bp.route("/budget/delete/<int:id>")
@login_required
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    if budget.user_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard.budget"))

    db.session.delete(budget)
    db.session.commit()
    flash("Budget deleted successfully.", "success")
    return redirect(url_for("dashboard.budget"))


@dashboard_bp.route('/insights')
@login_required
def insights():
    current_month = datetime.now().strftime('%B')

    insights_data = {
        'month': current_month,
        'spending_trend': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'data': [12000, 15000, 11000, 13000, 14000, 12500]
        },
        'category_breakdown': {
            'labels': ['Food', 'Transport', 'Entertainment', 'Bills', 'Others'],
            'data': [35, 25, 15, 15, 10]
        },
        'savings_rate': 0.25
    }

    return render_template('insights.html', insights=insights_data)


@dashboard_bp.route('/export/csv')
@login_required
def export_csv():
    try:
        transactions = Transaction.query.filter_by(
            user_id=current_user.id
        ).order_by(Transaction.date.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Date', 'Description', 'Amount', 'Type',
            'Category', 'Payment Method', 'Tags', 'Notes', 'Created At'
        ])

        for trans in transactions:
            writer.writerow([
                trans.date.strftime('%Y-%m-%d') if trans.date else '',
                trans.description or '',
                float(trans.amount) if trans.amount else 0.0,
                trans.type or '',
                trans.category.name if trans.category else 'Uncategorized',
                trans.payment_method or '',
                trans.tags or '',
                trans.notes or '',
                trans.created_at.strftime('%Y-%m-%d %H:%M:%S') if trans.created_at else ''
            ])

        output.seek(0)
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"transactions_export_{date_str}.csv"

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-type'] = 'text/csv'
        return response

    except Exception as e:
        print(f"[EXPORT ERROR] {e}")
        flash('Error generating export file', 'error')
        return redirect(url_for('dashboard.transactions'))

@dashboard_bp.route('/export/pdf')
@login_required
def export_pdf():
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()

        if not transactions:
            flash("No transactions to export.", "warning")
            return redirect(url_for('dashboard.export'))  # FIXED

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30, y, "Transaction Report")  # FIXED name error
        y -= 30

        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(30, y, "Date")
        pdf.drawString(90, y, "Type")
        pdf.drawString(140, y, "Amount")
        pdf.drawString(200, y, "Category")
        pdf.drawString(300, y, "Description")
        y -= 20

        pdf.setFont("Helvetica", 9)
        for tx in transactions:
            if y < 50:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(30, y, "Date")
                pdf.drawString(90, y, "Type")
                pdf.drawString(140, y, "Amount")
                pdf.drawString(200, y, "Category")
                pdf.drawString(300, y, "Description")
                y -= 20
                pdf.setFont("Helvetica", 9)

            pdf.drawString(30, y, tx.date.strftime('%Y-%m-%d'))
            pdf.drawString(90, y, tx.type)
            pdf.drawString(140, y, f"₹{float(tx.amount):.2f}")
            pdf.drawString(200, y, tx.category.name if tx.category else "Uncategorized")
            pdf.drawString(300, y, (tx.description or "N/A")[:40])
            y -= 15

        pdf.save()
        buffer.seek(0)

        filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    except Exception as e:
        import traceback
        print("PDF export error:", e)
        traceback.print_exc()
        flash("Error generating PDF export. Please try again later.", "danger")
        return redirect(url_for('dashboard.export'))  # FIXED


class UpdateProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = FileField('Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    update_profile = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')
    ])
    change_password = SubmitField('Change Password')

import os

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm()
    password_form = PasswordChangeForm()

    # ✅ Handle Profile Update
    if profile_form.validate_on_submit() and 'username' in request.form:
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data

        # ✅ Handle Avatar upload if provided
        avatar = request.files.get('avatar')
        if avatar and avatar.filename != "":
            # ✅ Ensure upload folder exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            filename = f"user_{current_user.id}_avatar.png"
            avatar_path = os.path.join(UPLOAD_FOLDER, filename)

            avatar.save(avatar_path)

            # ✅ Store relative URL
            current_user.avatar_url = url_for('static', filename=f'uploads/{filename}')

        db.session.commit()
        flash("✅ Profile updated successfully!", "success")
        return redirect(url_for('dashboard.profile'))

    # ✅ Handle Password Change
    if password_form.validate_on_submit() and 'current_password' in request.form:
        from werkzeug.security import check_password_hash, generate_password_hash

        if not check_password_hash(current_user.password, password_form.current_password.data):
            flash("❌ Current password is incorrect", "danger")
        elif password_form.new_password.data != password_form.confirm_password.data:
            flash("❌ New passwords do not match", "danger")
        else:
            current_user.password = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash("✅ Password updated successfully!", "success")
            return redirect(url_for('dashboard.profile'))

    # ✅ Pre-fill profile form with current user details
    profile_form.username.data = current_user.username
    profile_form.email.data = current_user.email

    return render_template(
        'profile.html',
        profile_form=profile_form,
        password_form=password_form
    )


@dashboard_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    confirm_email = request.form.get('confirm_email')
    confirm_delete = request.form.get('confirm_delete') == 'on'

    if not confirm_delete or confirm_email != current_user.email:
        flash('Account deletion not confirmed', 'danger')
        return redirect(url_for('dashboard.profile'))

    # Optional: perform actual deletion of related data here

    flash('Account deletion would be processed here', 'info')
    return redirect(url_for('auth.logout'))