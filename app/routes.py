from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from .models import Document, PropertyData, MarketTrend, AnalyzedDeal
from .document_processor import save_file, extract_text_from_image, generate_tags, generate_property_description
import json
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from datetime import datetime, date
from . import db
from .ml_model import predict

main = Blueprint('main', __name__)
CORS(main)

@main.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/property_description_generator', methods=['GET', 'POST'])
def property_description_generator():
    if request.method == 'POST':
        if 'photos' not in request.files:
            return jsonify({'error': 'No photos provided'}), 400

        photos = request.files.getlist('photos')
        photo_descriptions = []
        photo_info = []

        for photo in photos:
            if photo and allowed_file(photo.filename):
                filename, file_path = save_file(photo)
                
                description = extract_text_from_image(file_path)
                tags = generate_tags(description)

                photo_descriptions.append(description)
                photo_info.append({
                    'filename': filename,
                    'file_path': url_for('main.uploaded_file', filename=filename, _external=True),
                    'tags': tags
                })

        if not photo_descriptions:
            return jsonify({'error': 'No valid photos provided'}), 400

        combined_description = "\n".join(photo_descriptions)
        property_description = generate_property_description(combined_description)

        return jsonify({
            'description': property_description,
            'photo_info': photo_info
        })

    return render_template('property_description_generator.html')

def generate_property_description(combined_description):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional real estate agent. Generate a compelling property description based on the following information."},
            {"role": "user", "content": f"Generate a property description based on this information:\n\n{combined_description}"}
        ]
    )
    
    return response.choices[0].message.content.strip()

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
            
            if file.content_type.startswith('image/'):
                description = extract_text_from_image(file_path)
                tags = generate_tags(description)
            else:
                description = ""
                tags = []

            new_document = Document(
                filename=filename,
                file_path=file_path,
                file_type=file.content_type,
                extracted_text=description,
                tags=', '.join(tags)
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

@main.route('/cash_flow_calculator', methods=['GET', 'POST'])
def cash_flow_calculator():
    if request.method == 'POST':
        # Process form data and calculate cash flow
        # For now, we'll just return a dummy response
        return jsonify({'cash_flow': 1000})
    return render_template('cash_flow_calculator.html')

@main.route('/roi_calculator', methods=['GET', 'POST'])
def roi_calculator():
    if request.method == 'POST':
        # Process form data and calculate ROI
        # For now, we'll just return a dummy response
        return jsonify({'roi': 10})
    return render_template('roi_calculator.html')

@main.route('/property_comparison', methods=['GET', 'POST'])
def property_comparison():
    if request.method == 'POST':
        # Process form data and compare properties
        # For now, we'll just return a dummy response
        return jsonify({'comparison': 'Property A is better'})
    return render_template('property_comparison.html')

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main.route('/deal_analyzer', methods=['GET', 'POST'])
def deal_analyzer():
    if request.method == 'POST':
        try:
            # Get form data
            purchase_price = float(request.form.get('purchase_price', 0))
            down_payment = float(request.form.get('down_payment', 0))
            interest_rate = float(request.form.get('interest_rate', 0)) / 100
            monthly_rental_income = float(request.form.get('monthly_rental_income', 0))
            monthly_operating_expenses = float(request.form.get('monthly_operating_expenses', 0))
            vacancy_rate = float(request.form.get('vacancy_rate', 0)) / 100

            # Calculations
            loan_amount = purchase_price - down_payment
            annual_rental_income = monthly_rental_income * 12 * (1 - vacancy_rate)
            annual_operating_expenses = monthly_operating_expenses * 12
            net_operating_income = annual_rental_income - annual_operating_expenses
            annual_debt_service = loan_amount * interest_rate  # Simplified calculation
            annual_cash_flow = net_operating_income - annual_debt_service
            total_investment = down_payment
            roi = (annual_cash_flow / total_investment) * 100 if total_investment else 0
            cap_rate = (net_operating_income / purchase_price) * 100 if purchase_price else 0
            cash_on_cash_return = roi

            # Use ML model to predict cash flow
            market_trend = MarketTrend.query.order_by(MarketTrend.date.desc()).first()
            if not market_trend:
                raise ValueError("No market trend data available.")
            
            input_features = [
                purchase_price,
                monthly_rental_income,
                monthly_operating_expenses,
                vacancy_rate,
                market_trend.median_home_price,
                market_trend.rental_rate,
                market_trend.unemployment_rate
            ]
            predicted_cash_flow = predict(input_features)

            # Save the analyzed deal
            new_deal = AnalyzedDeal(
                purchase_price=purchase_price,
                down_payment=down_payment,
                interest_rate=interest_rate * 100,  # Store as percentage
                monthly_rental_income=monthly_rental_income,
                monthly_operating_expenses=monthly_operating_expenses,
                vacancy_rate=vacancy_rate * 100,  # Store as percentage
                roi=roi,
                cap_rate=cap_rate,
                cash_on_cash_return=cash_on_cash_return,
                annual_cash_flow=annual_cash_flow,
                predicted_cash_flow=predicted_cash_flow
            )
            db.session.add(new_deal)
            db.session.commit()

            # Render results with visualization
            return render_template('deal_analyzer.html', 
                                   results=new_deal.to_dict(),
                                   saved_deals=get_saved_deals())
        except Exception as e:
            return render_template('deal_analyzer.html', error=str(e), saved_deals=get_saved_deals())
    return render_template('deal_analyzer.html', saved_deals=get_saved_deals())

def get_saved_deals():
    return [deal.to_dict() for deal in AnalyzedDeal.query.order_by(AnalyzedDeal.analysis_date.desc()).limit(5)]

@main.route('/api/saved_deals', methods=['GET'])
def api_saved_deals():
    return jsonify(get_saved_deals())

@main.route('/populate_sample_data')
def populate_sample_data():
    from .ml_model import predict  # Ensure all imports are correct
    # Sample Property Data
    if not PropertyData.query.first():
        sample_properties = [
            PropertyData(
                address="123 Maple Street",
                purchase_price=250000,
                rental_income=2000,
                operating_expenses=800,
                vacancy_rate=0.05,
                purchase_date=date(2022, 1, 15)
            ),
            PropertyData(
                address="456 Oak Avenue",
                purchase_price=350000,
                rental_income=2500,
                operating_expenses=900,
                vacancy_rate=0.04,
                purchase_date=date(2021, 6, 10)
            ),
            # Add more sample properties as needed
        ]
        db.session.add_all(sample_properties)
        db.session.commit()

    # Sample Market Trends
    if not MarketTrend.query.first():
        sample_trends = [
            MarketTrend(
                date=date(2023, 1, 1),
                median_home_price=300000,
                rental_rate=2.5,
                unemployment_rate=5.0
            ),
            MarketTrend(
                date=date(2023, 6, 1),
                median_home_price=310000,
                rental_rate=2.6,
                unemployment_rate=4.8
            ),
            # Add more sample trends as needed
        ]
        db.session.add_all(sample_trends)
        db.session.commit()

    return jsonify({'message': 'Sample data populated successfully.'}), 200

@main.route('/api/predict_cash_flow', methods=['POST'])
def predict_cash_flow():
    data = request.json
    purchase_price = data.get('purchase_price')
    rental_income = data.get('rental_income')
    operating_expenses = data.get('operating_expenses')
    vacancy_rate = data.get('vacancy_rate') / 100
    median_home_price = data.get('median_home_price')
    rental_rate = data.get('rental_rate')
    unemployment_rate = data.get('unemployment_rate')

    input_features = [
        purchase_price,
        rental_income,
        operating_expenses,
        vacancy_rate,
        median_home_price,
        rental_rate,
        unemployment_rate
    ]

    prediction = predict(input_features)

    return jsonify({'predicted_cash_flow': prediction}), 200

