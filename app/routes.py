from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import os
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from .models import db, PropertyDescription, CashFlowCalculation, PropertyComparison, ROICalculation
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
        if 'photos' not in request.files:
            return jsonify({'error': 'No photos provided'}), 400

        photos = request.files.getlist('photos')
        image_messages = []
        saved_image_paths = []

        # Print the UPLOAD_FOLDER path for debugging
        print(f"Accessing UPLOAD_FOLDER: {current_app.config.get('UPLOAD_FOLDER', 'Not set')}")

        UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER')
        if not UPLOAD_FOLDER:
            return jsonify({'error': 'Upload folder not configured'}), 500

        for photo in photos:
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                photo.save(file_path)
                # Update this line to use url_for
                saved_image_paths.append(url_for('static', filename=f'uploads/{filename}'))
                
                # Encode the image
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
                image_messages.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_string}"
                    }
                })

        if not image_messages:
            return jsonify({'error': 'No valid photos provided'}), 400

        # Prepare messages for the API
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are a professional real estate agent. Analyze the provided images and generate a compelling property description."},
            {"role": "user", "content": [
                {"type": "text", "text": "Please describe this property based on the images provided."},
                *image_messages
            ]}
        ]

        try:
            # Generate description using OpenAI API with the specified model
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300
            )

            description = response.choices[0].message.content.strip()
            
            # Save the description to the database
            new_description = PropertyDescription(
                description=description,
                image_paths=','.join(saved_image_paths),
                created_at=datetime.utcnow()
            )
            db.session.add(new_description)
            db.session.commit()

            return jsonify({
                'description': description,
                'images': saved_image_paths
            })

        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return jsonify({'error': 'An error occurred while generating the description. Please try again later.'}), 500

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

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Comment out other routes for now