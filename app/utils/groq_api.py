import os
import requests
from flask_login import current_user
from app.models import Expense, Income, Transaction, Budget, Category
from sqlalchemy import func, extract
from app import db
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama3-70b-8192"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}   

def get_user_financial_summary(user_id):
    now = datetime.now()

    # Totals
    total_expense = db.session.query(func.sum(Expense.amount)).filter_by(user_id=user_id).scalar() or 0
    total_income = db.session.query(func.sum(Income.amount)).filter_by(user_id=user_id).scalar() or 0

    # Monthly
    monthly_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        extract('month', Transaction.date) == now.month,
        extract('year', Transaction.date) == now.year
    ).scalar() or 0

    monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        extract('month', Transaction.date) == now.month,
        extract('year', Transaction.date) == now.year
    ).scalar() or 0

    # Budgets
    budgets = Budget.query.filter_by(user_id=user_id).all()
    budget_info = {b.category.name if b.category else 'Uncategorized': b.amount for b in budgets}

    # Category-wise spending
    category_spending = db.session.query(
        Category.name, func.sum(Expense.amount)
    ).join(Expense.category).filter(
        Expense.user_id == user_id
    ).group_by(Category.name).all()

    category_summary = {name: float(amount) for name, amount in category_spending}

    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "monthly_income": float(monthly_income),
        "monthly_expense": float(monthly_expense),
        "category_spending": category_summary,
        "budgets": budget_info
    }

def format_insight_prompt(data):
    category_lines = "\n".join([f"- {cat}: ₹{amt:.2f}" for cat, amt in data['category_spending'].items()])
    budget_lines = "\n".join([f"- {cat}: ₹{limit:.2f}" for cat, limit in data['budgets'].items()])

    return f"""
You are a smart financial assistant. Analyze this user's financial activity and give actionable suggestions.

Total Income: ₹{data['total_income']:.2f}
Total Expenses: ₹{data['total_expense']:.2f}
Monthly Income: ₹{data['monthly_income']:.2f}
Monthly Expenses: ₹{data['monthly_expense']:.2f}

Spending by Category:
{category_lines or 'None'}

Budgets Set by User:
{budget_lines or 'None'}

Please provide:
1. Spending pattern summary
2. Budget evaluation
3. Personalized advice to improve savings and reduce unnecessary spending
""".strip()

def get_financial_insights(user_id):
    if not GROQ_API_KEY:
        return "GROQ API key not configured."

    try:
        data = get_user_financial_summary(user_id)
        prompt = format_insight_prompt(data)

        payload = {
            "model": GROQ_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens":1024,
            "top_p":1,
            "stop":None
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        return f"Groq API error: {str(e)}"
    except (KeyError, IndexError) as e:
        return "Failed to parse response from Groq API."
    except Exception as e:
        return f"Unexpected error: {str(e)}"