from flask import Blueprint, Response
from flask_login import login_required, current_user
from app.models import Transaction
import csv
import io

export_bp = Blueprint('report', __name__, url_prefix='/report')

@export_bp.route('/export_csv')
@login_required
def export_csv():
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Type', 'Category', 'Description', 'Amount', 'Payment Method', 'Tags', 'Notes'])

        for t in transactions:
            writer.writerow([
            t.date.strftime('%Y-%m-%d'),
            t.type.capitalize(),
            t.category.name if t.category else '',
            t.description or '',
            float(t.amount),
            t.payment_method or '',
            t.tags or '',
            t.notes or ''
        ])

        output.seek(0)
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=transactions_user_{current_user.id}.csv'}
            )
        
    except Exception as e:
        return f"Error generating export file: {str(e)}", 500

