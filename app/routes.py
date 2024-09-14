from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file
from werkzeug.utils import secure_filename
import os
from .models import db, PropertyDescription, CashFlowCalculation, PropertyComparison, ROICalculation, Document
from .document_processor import save_file, extract_text, generate_tags
import json
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from datetime import datetime

main = Blueprint('main', __name__)

# Initialize the OpenAI client with the provided API key
client = OpenAI(api_key='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')

@main.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/property_description_generator', methods=['GET', 'POST'])
def property_description_generator():
    if request.method == 'POST':
        # Handle POST request (file upload and description generation)
        if 'photos' not in request.files:
            return jsonify({'error': 'No photos provided'}), 400

        photos = request.files.getlist('photos')
        photo_descriptions = []

        for photo in photos:
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                file_path = save_file(photo)
                
                extracted_text = extract_text(file_path)
                tags = generate_tags(extracted_text)

                photo_descriptions.append({
                    'filename': filename,
                    'extracted_text': extracted_text,
                    'tags': tags
                })

        if not photo_descriptions:
            return jsonify({'error': 'No valid photos provided'}), 400

        # Here you would typically use the OpenAI API to generate a description
        # For now, we'll just return a placeholder
        generated_description = "This is a placeholder for the generated property description."

        return jsonify({
            'description': generated_description,
            'photo_descriptions': photo_descriptions
        })

    return render_template('property_description_generator.html')

@main.route('/saved_descriptions')
def saved_descriptions():
    descriptions = PropertyDescription.query.order_by(PropertyDescription.created_at.desc()).all()
    return render_template('saved_descriptions.html', descriptions=descriptions)

@main.route('/cash_flow_calculator', methods=['GET', 'POST'])
def cash_flow_calculator():
    if request.method == 'POST':
        property_name = request.form.get('property_name')
        purchase_price = float(request.form.get('purchase_price'))
        rental_income = float(request.form.get('rental_income'))
        expenses = float(request.form.get('expenses'))
        mortgage_payment = float(request.form.get('mortgage_payment'))

        cash_flow = rental_income - expenses - mortgage_payment

        calculation = CashFlowCalculation(
            property_name=property_name,
            purchase_price=purchase_price,
            rental_income=rental_income,
            expenses=expenses,
            mortgage_payment=mortgage_payment,
            cash_flow=cash_flow
        )
        db.session.add(calculation)
        db.session.commit()

        return jsonify({
            'cash_flow': cash_flow,
            'id': calculation.id
        })

    return render_template('cash_flow_calculator.html')

@main.route('/saved_calculations')
def saved_calculations():
    calculations = CashFlowCalculation.query.order_by(CashFlowCalculation.created_at.desc()).all()
    return render_template('saved_calculations.html', calculations=calculations)

@main.route('/delete_calculation/<int:id>', methods=['POST'])
def delete_calculation(id):
    calculation = CashFlowCalculation.query.get_or_404(id)
    db.session.delete(calculation)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/property_comparison', methods=['GET', 'POST'])
def property_comparison():
    if request.method == 'POST':
        new_property = PropertyComparison(
            property_name=request.form['property_name'],
            purchase_price=float(request.form['purchase_price']),
            square_footage=float(request.form['square_footage']),
            num_bedrooms=int(request.form['num_bedrooms']),
            num_bathrooms=float(request.form['num_bathrooms']),
            year_built=int(request.form['year_built']),
            location=request.form['location'],
            estimated_rent=float(request.form['estimated_rent'])
        )
        db.session.add(new_property)
        db.session.commit()
        return jsonify({'success': True, 'id': new_property.id})

    properties = PropertyComparison.query.order_by(PropertyComparison.created_at.desc()).all()
    return render_template('property_comparison.html', properties=properties)

@main.route('/delete_property_comparison/<int:id>', methods=['POST'])
def delete_property_comparison(id):
    property_comparison = PropertyComparison.query.get_or_404(id)
    db.session.delete(property_comparison)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/roi_calculator', methods=['GET', 'POST'])
def roi_calculator():
    if request.method == 'POST':
        purchase_price = float(request.form['purchase_price'])
        closing_costs = float(request.form['closing_costs'])
        rehab_costs = float(request.form['rehab_costs'])
        annual_rental_income = float(request.form['annual_rental_income'])
        annual_expenses = float(request.form['annual_expenses'])
        appreciation_rate = float(request.form['appreciation_rate']) / 100
        holding_period = int(request.form['holding_period'])

        total_investment = purchase_price + closing_costs + rehab_costs
        total_profit = 0
        for year in range(holding_period):
            annual_cash_flow = annual_rental_income - annual_expenses
            appreciation = purchase_price * (1 + appreciation_rate) ** year - purchase_price
            total_profit += annual_cash_flow + appreciation

        roi = (total_profit / total_investment) * 100

        new_calculation = ROICalculation(
            property_name=request.form['property_name'],
            purchase_price=purchase_price,
            closing_costs=closing_costs,
            rehab_costs=rehab_costs,
            annual_rental_income=annual_rental_income,
            annual_expenses=annual_expenses,
            appreciation_rate=appreciation_rate * 100,
            holding_period=holding_period,
            roi=roi
        )
        db.session.add(new_calculation)
        db.session.commit()

        return jsonify({
            'roi': roi,
            'id': new_calculation.id
        })

    calculations = ROICalculation.query.order_by(ROICalculation.created_at.desc()).all()
    return render_template('roi_calculator.html', calculations=calculations)

@main.route('/delete_roi_calculation/<int:id>', methods=['POST'])
def delete_roi_calculation(id):
    calculation = ROICalculation.query.get_or_404(id)
    db.session.delete(calculation)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/document_organizer', methods=['GET', 'POST'])
def document_organizer():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = save_file(file)
            
            extracted_text = extract_text(file_path)
            tags = generate_tags(extracted_text)

            new_document = Document(
                filename=filename,
                file_path=file_path,
                file_type=file.content_type,
                extracted_text=extracted_text,
                tags=json.dumps(tags),
                property_id=None  # Set to None or get a property_id from the form if needed
            )
            db.session.add(new_document)
            db.session.commit()

            return jsonify({'success': True, 'document_id': new_document.id}), 201
        
    documents = Document.query.order_by(Document.upload_date.desc()).all()
    return render_template('document_organizer.html', documents=documents)

@main.route('/document/<int:document_id>')
def get_document(document_id):
    document = Document.query.get_or_404(document_id)
    return jsonify({
        'id': document.id,
        'filename': document.filename,
        'file_type': document.file_type,
        'upload_date': document.upload_date.isoformat(),
        'tags': json.loads(document.tags),
        'version': document.version
    })

@main.route('/document/<int:document_id>/download')
def download_document(document_id):
    document = Document.query.get_or_404(document_id)
    return send_file(document.file_path, as_attachment=True, attachment_filename=document.filename)

@main.route('/document/search')
def search_documents():
    query = request.args.get('q', '')
    documents = Document.query.filter(
        (Document.filename.ilike(f'%{query}%')) |
        (Document.tags.ilike(f'%{query}%')) |
        (Document.extracted_text.ilike(f'%{query}%'))
    ).all()
    return jsonify([{
        'id': doc.id,
        'filename': doc.filename,
        'file_type': doc.file_type,
        'upload_date': doc.upload_date.isoformat(),
        'tags': json.loads(doc.tags)
    } for doc in documents])

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Comment out other routes for now