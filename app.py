from flask import Flask, render_template, request, jsonify, flash, send_from_directory, redirect, url_for
import os
from werkzeug.utils import secure_filename
import openai
from datetime import datetime

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

openai.api_key = 'your_openai_api_key_here'  # Replace with your actual OpenAI API key

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/property_description_generator', methods=['GET', 'POST'])
def property_description_generator():
    if request.method == 'POST':
        if 'photos' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        photos = request.files.getlist('photos')
        uploaded_files = []
        
        for photo in photos:
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(file_path)
                uploaded_files.append({
                    'filename': filename,
                    'file_path': f'/static/uploads/{filename}'
                })
        
        if not uploaded_files:
            return jsonify({'error': 'No valid images uploaded'}), 400

        property_type = request.form.get('property_type')
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        square_footage = request.form.get('square_footage')
        year_built = request.form.get('year_built')
        location = request.form.get('location')
        additional_features = request.form.get('additional_features')

        property_details = f"""
        Property Type: {property_type}
        Bedrooms: {bedrooms}
        Bathrooms: {bathrooms}
        Square Footage: {square_footage}
        Year Built: {year_built}
        Location: {location}
        Additional Features: {additional_features}
        Number of Photos: {len(uploaded_files)}
        """

        # Generate description using GPT-4o-mini
        prompt = f"Generate a compelling property description based on the following details:\n\n{property_details}"
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional real estate agent. Generate a compelling property description."},
                {"role": "user", "content": prompt}
            ]
        )
        generated_description = response.choices[0].message.content.strip()
        
        return jsonify({
            'description': generated_description,
            'photo_info': uploaded_files
        })
    
    current_year = datetime.now().year
    return render_template('property_description_generator.html', current_year=current_year)

@app.route('/cash_flow_calculator', methods=['GET', 'POST'])
def cash_flow_calculator():
    if request.method == 'POST':
        data = request.json
        # Here you would typically save the data to a database
        # For now, we'll just return the data as-is
        return jsonify(data)
    return render_template('cash_flow_calculator.html')

@app.route('/roi_calculator', methods=['GET', 'POST'])
def roi_calculator():
    if request.method == 'POST':
        data = request.json
        initial_investment = float(data['initial_investment'])
        annual_return = float(data['annual_return'])
        investment_period = float(data['investment_period'])
        
        total_return = annual_return * investment_period
        roi = (total_return - initial_investment) / initial_investment * 100
        
        result = {
            'roi': roi,
            'total_return': total_return,
            'initial_investment': initial_investment,
            'annual_return': annual_return,
            'investment_period': investment_period
        }
        
        # Here you would typically save the data to a database
        # For now, we'll just return the calculated results
        return jsonify(result)
    return render_template('roi_calculator.html')

@app.route('/property_comparison', methods=['GET', 'POST'])
def property_comparison():
    if request.method == 'POST':
        # Process form data for property comparison
        # The actual comparison is now done client-side, so we don't need server-side processing
        return jsonify({'success': True})
    return render_template('property_comparison.html')

@app.route('/document_organizer', methods=['GET', 'POST'])
def document_organizer():
    if request.method == 'POST':
        # Here you would typically process the uploaded document
        # For now, we'll just return a success message
        return jsonify({'message': 'Document uploaded successfully'})
    return render_template('document_organizer.html')

@app.route('/deal_analyzer', methods=['GET', 'POST'])
def deal_analyzer():
    if request.method == 'POST':
        # Here you would process the form data and perform the deal analysis
        # For now, we'll just return a dummy response
        return jsonify({'message': 'Deal analysis completed'})
    return render_template('deal_analyzer.html')

@app.route('/syndication_tool', methods=['GET', 'POST'])
def syndication_tool():
    # This is a placeholder for the deals data
    deals = [
        {
            'id': 1,
            'title': 'Sample Deal 1',
            'target_amount': 1000000,
            'current_amount': 750000
        },
        {
            'id': 2,
            'title': 'Sample Deal 2',
            'target_amount': 500000,
            'current_amount': 250000
        }
    ]
    
    if request.method == 'POST':
        # Handle form submission (create new deal)
        # This is just a placeholder, you'll need to implement the actual logic
        flash('New deal created successfully!', 'success')
        return redirect(url_for('syndication_tool'))
    
    return render_template('syndication/dashboard.html', deals=deals)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)