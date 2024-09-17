from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from . import db
from .models import Deal, Investment, DealDocument
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

syndication = Blueprint('syndication', __name__)

@syndication.route('/', methods=['GET'])
def syndication_dashboard():
    deals = Deal.query.order_by(Deal.created_at.desc()).all()
    return render_template('syndication.html', deals=deals)

@syndication.route('/create_deal', methods=['POST'])
def create_deal():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        target_amount = float(request.form.get('target_amount'))
        
        new_deal = Deal(title=title, description=description, target_amount=target_amount)
        db.session.add(new_deal)
        db.session.commit()
        
        flash('New deal created successfully!', 'success')
        return redirect(url_for('syndication.syndication_dashboard'))

@syndication.route('/deals/<int:deal_id>', methods=['GET'])
def view_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    return render_template('syndication/view_deal.html', deal=deal)

@syndication.route('/deals/<int:deal_id>/invest', methods=['POST'])
def invest(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    amount = float(request.form.get('amount'))
    
    if amount <= 0:
        flash('Investment amount must be positive.', 'error')
        return redirect(url_for('syndication.view_deal', deal_id=deal_id))
    
    if deal.current_amount + amount > deal.target_amount:
        flash('Investment would exceed the deal target amount.', 'error')
        return redirect(url_for('syndication.view_deal', deal_id=deal_id))
    
    investment = Investment(deal_id=deal_id, amount=amount)
    deal.current_amount += amount
    db.session.add(investment)
    db.session.commit()
    
    flash('Investment successful!', 'success')
    return redirect(url_for('syndication.view_deal', deal_id=deal_id))

@syndication.route('/deals/<int:deal_id>/upload_document', methods=['POST'])
def upload_document(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    
    if 'document' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('syndication.view_deal', deal_id=deal_id))
    
    file = request.files['document']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('syndication.view_deal', deal_id=deal_id))
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        document = DealDocument(deal_id=deal_id, filename=filename, file_path=file_path)
        db.session.add(document)
        db.session.commit()
        
        flash('Document uploaded successfully!', 'success')
    
    return redirect(url_for('syndication.view_deal', deal_id=deal_id))

@syndication.route('/deals/<int:deal_id>/share', methods=['POST'])
def share_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    recipient_email = request.form.get('email')
    
    # Simulate sending an email
    try:
        msg = MIMEText(f"Check out this deal: {deal.title}\n\n{deal.description}")
        msg['Subject'] = f"Deal: {deal.title}"
        msg['From'] = 'noreply@realestateplatform.com'
        msg['To'] = recipient_email

        # Simulate email sending (replace with actual email sending logic)
        print(f"Sending email to {recipient_email}:\n{msg.as_string()}")

        flash('Deal shared successfully!', 'success')
    except Exception as e:
        flash(f'Failed to share deal: {str(e)}', 'error')
    
    return redirect(url_for('syndication.view_deal', deal_id=deal_id))

@syndication.route('/investor_dashboard')
def investor_dashboard():
    investments = Investment.query.all()
    return render_template('syndication/investor_dashboard.html', investments=investments)