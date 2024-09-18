from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from .models import Document, PropertyData, MarketTrend, AnalyzedDeal, Deal, Investment, User
from .document_processor import save_file, extract_text_from_image, generate_tags, generate_property_description
import base64
import openai
from . import db  # Import db from the app package
from .ml_model import predict  # Add this import at the top of the file
from datetime import date, datetime
import json  # Add this import at the top of the file

# Set the OpenAI API key
openai.api_key = os.environ['OPENAI_KEY']

main = Blueprint('main', __name__)
CORS(main)

@main.route('/')
@main.route('/index')
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
        photo_info = []
        image_contents = []

        for photo in photos:
            if photo and allowed_file(photo.filename):
                filename, file_path = save_file(photo)
                
                # Read the image file and encode it to base64
                with open(file_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Add image content for the vision model
                image_contents.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{encoded_image}"
                })

                photo_info.append({
                    'filename': filename,
                    'file_path': url_for('main.uploaded_file', filename=filename, _external=True)
                })

        if not image_contents:
            return jsonify({'error': 'No valid photos provided'}), 400

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a professional real estate agent. Analyze the provided images and generate a compelling property description based on what you see."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Generate a comprehensive and appealing property description. Include details about the property's features, style, condition, and any standout elements you observe in the following images."
                        },
                        *image_contents
                    ]
                }
            ]

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300
            )
            
            property_description = response.choices[0].message.content.strip()

            return jsonify({
                'description': property_description,
                'photo_info': photo_info
            })
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return render_template('property_description_generator.html')

@main.route('/document_organizer', methods=['GET', 'POST'])
def document_organizer():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename, file_path = save_file(file)
            
            # Extract text and generate tags
            if file.content_type.startswith('image/'):
                extracted_text = extract_text_from_image(file_path)
            else:
                # For non-image files, you might want to implement a different text extraction method
                extracted_text = "Text extraction not supported for this file type."
            
            tags = generate_tags(extracted_text)

            # Create a new Document instance and save to database
            new_document = Document(
                filename=filename,
                file_path=file_path,
                file_type=file.content_type,
                extracted_text=extracted_text,
                tags=json.dumps(tags)  # Store tags as a JSON string
            )
            db.session.add(new_document)
            db.session.commit()

            return jsonify({
                'success': True, 
                'document_id': new_document.id,
                'filename': filename,
                'file_type': file.content_type,
                'tags': tags
            }), 201
        
        return jsonify({'error': 'Invalid file type'}), 400

    # GET request: Fetch and display all documents
    documents = Document.query.order_by(Document.upload_date.desc()).all()
    documents_data = []
    for document in documents:
        doc_data = document.__dict__.copy()
        doc_data.pop('_sa_instance_state', None)  # Remove SQLAlchemy internal state
        doc_data['upload_date'] = doc_data['upload_date'].strftime('%Y-%m-%d %H:%M:%S')
        doc_data['tags'] = json.loads(document.tags) if document.tags else []
        documents_data.append(doc_data)
    return render_template('document_organizer.html', documents=documents_data)

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
        data = request.json
        initial_investment = float(data.get('initial_investment', 0))
        annual_return = float(data.get('annual_return', 0))
        investment_period = float(data.get('investment_period', 0))

        # Calculate ROI
        total_return = annual_return * investment_period
        roi = ((total_return - initial_investment) / initial_investment) * 100

        result = {
            'roi': round(roi, 2),
            'total_return': round(total_return, 2),
            'initial_investment': initial_investment,
            'annual_return': annual_return,
            'investment_period': investment_period
        }

        # Save calculation (you might want to implement this)
        # save_calculation(result)

        return jsonify(result)

    saved_calculations = []  # Or fetch saved calculations from your database
    return render_template('roi_calculator.html', saved_calculations=saved_calculations)

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

            # Fetch the latest market trend data
            market_trend = MarketTrend.query.order_by(MarketTrend.date.desc()).first()
            if not market_trend:
                # If no market trend data is available, use default values
                median_home_price = 300000  # Example default value
                rental_rate = 2.5  # Example default value
                unemployment_rate = 5.0  # Example default value
            else:
                median_home_price = market_trend.median_home_price
                rental_rate = market_trend.rental_rate
                unemployment_rate = market_trend.unemployment_rate

            input_features = [
                purchase_price,
                monthly_rental_income,
                monthly_operating_expenses,
                vacancy_rate,
                median_home_price,
                rental_rate,
                unemployment_rate
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
    # Check if data already exists
    if PropertyData.query.first() is None:
        # Sample Property Data
        sample_properties = [
            PropertyData(
                property_name="Maple Street Residence",
                address="123 Maple Street",
                purchase_price=250000,
                rental_income=2000,
                operating_expenses=800,
                vacancy_rate=0.05,
                purchase_date=date(2022, 1, 15)
            ),
            PropertyData(
                property_name="Oak Avenue Apartment",
                address="456 Oak Avenue",
                purchase_price=300000,
                rental_income=2500,
                operating_expenses=1000,
                vacancy_rate=0.03,
                purchase_date=date(2022, 3, 1)
            ),
        ]
        db.session.add_all(sample_properties)
        db.session.commit()

    # Check if market trends data already exists
    if MarketTrend.query.first() is None:
        # Sample Market Trends
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

@main.route('/syndication')
def syndication():
    deals = Deal.query.all()  # Fetch all deals from the database
    return render_template('syndication.html', deals=deals)

@main.route('/api/deal/<int:deal_id>', methods=['GET'])
def get_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    return jsonify(deal.to_dict())

@main.route('/api/deal/create', methods=['POST'])
def create_deal():
    try:
        new_deal = Deal(
            name=request.form['name'],
            description=request.form['description'],
            target_raise=float(request.form['target_raise']),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            progress=0
        )
        db.session.add(new_deal)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Deal created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/deal/<int:deal_id>/documents', methods=['GET'])
def get_deal_documents(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    documents = [doc.to_dict() for doc in deal.documents]
    return jsonify({'documents': documents})

@main.route('/api/deal/<int:deal_id>/investors', methods=['GET'])
def get_deal_investors(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    investors = [inv.to_dict() for inv in deal.investments]
    return jsonify({'investors': investors})

@main.route('/api/document/upload', methods=['POST'])
def upload_document():
    try:
        deal_id = request.form['deal_id']
        deal = Deal.query.get_or_404(deal_id)
        file = request.files['document']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            new_document = Document(filename=filename, file_path=file_path, deal_id=deal_id)
            db.session.add(new_document)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Document uploaded successfully'})
        else:
            return jsonify({'success': False, 'error': 'Invalid file'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/investor/add', methods=['POST'])
def add_investor():
    try:
        deal_id = request.form['deal_id']
        deal = Deal.query.get_or_404(deal_id)
        new_investment = Investment(
            deal_id=deal_id,
            investor_email=request.form['email'],
            amount=float(request.form['amount'])
        )
        db.session.add(new_investment)
        deal.progress = (sum([inv.amount for inv in deal.investments]) / deal.target_raise) * 100
        db.session.commit()
        return jsonify({'success': True, 'message': 'Investor added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/chatbot_message', methods=['POST'])
def chatbot_message():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'response': 'Please enter a message.'}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant for a real estate investment platform. Provide helpful suggestions and summaries based on the user's data and questions."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300
        )

        ai_message = response.choices[0].message.content.strip()
        return jsonify({'response': ai_message})
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return jsonify({'response': 'Sorry, I encountered an error. Please try again later.'}), 500
