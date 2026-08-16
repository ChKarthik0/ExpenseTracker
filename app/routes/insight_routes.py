from flask import Blueprint, render_template, flash, jsonify
from flask_login import login_required, current_user
from app.utils.groq_api import get_financial_insights, get_user_financial_summary

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights')
@login_required
def insights():
    from app.utils.groq_api import get_user_financial_summary, get_financial_insights

    insights_data = get_financial_insights(current_user.id)
    summary_data = get_user_financial_summary(current_user.id)
    chart_data = get_user_financial_summary(current_user.id)
    return render_template('insights.html', insights=insights_data, chart_data=summary_data, chart=chart_data)

@insights_bp.route('/insights/generate', methods=['POST'])
@login_required
def generate_insights():
    try:
        insights_data = get_financial_insights(current_user.id)
        return jsonify({"success": True, "insights": insights_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})