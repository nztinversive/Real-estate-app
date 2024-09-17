from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Deal, DealDocument

import os

syndication = Blueprint('syndication', __name__)

@syndication.route('/dashboard', methods=['GET', 'POST'])
def syndication_dashboard():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        target_amount = float(request.form.get('target_amount'))
        
        new_deal = Deal(title=title, description=description, target_amount=target_amount)
        db.session.add(new_deal)
        db.session.commit()
        
        flash('New deal created successfully!', 'success')
        return redirect(url_for('syndication.syndication_dashboard'))

    active_deals = Deal.query.all()
    return render_template('syndication/dashboard.html', deals=active_deals)

@syndication.route('/deal/<int:deal_id>')
def deal_details(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    return render_template('syndication/deal_details.html', deal=deal)

@syndication.route('/deal/<int:deal_id>/invest', methods=['POST'])
def invest(deal_id):
    # TODO: Implement investment logic
    return redirect(url_for('syndication.deal_details', deal_id=deal_id))

@syndication.route('/deal/<int:deal_id>/share', methods=['POST'])
def share_deal(deal_id):
    # TODO: Implement deal sharing logic
    return redirect(url_for('syndication.deal_details', deal_id=deal_id))

@syndication.route('/deal/<int:deal_id>/delete', methods=['POST'])
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    db.session.delete(deal)
    db.session.commit()
    flash('Deal deleted successfully!', 'success')
    return redirect(url_for('syndication.syndication_dashboard'))

@syndication.route('/deal/<int:deal_id>/upload', methods=['POST'])
def upload_document(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('syndication.deal_details', deal_id=deal_id))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('syndication.deal_details', deal_id=deal_id))
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_type = file.content_type
        new_document = DealDocument(deal_id=deal_id, filename=filename, file_path=file_path, file_type=file_type)
        db.session.add(new_document)
        db.session.commit()
        flash('File uploaded successfully', 'success')
    return redirect(url_for('syndication.deal_details', deal_id=deal_id))

@syndication.route('/deal/<int:deal_id>/document/<int:document_id>')
def view_document(deal_id, document_id):
    document = DealDocument.query.get_or_404(document_id)
    return send_file(document.file_path, as_attachment=True)