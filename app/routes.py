from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file, send_from_directory
from flask_cors import CORS  # Add this import
from werkzeug.utils import secure_filename
import os
from .models import Document
from .document_processor import save_file, extract_text_from_image, generate_tags, generate_property_description
import json
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from datetime import datetime
from . import db

main = Blueprint('main', __name__)
CORS(main)  # Add this line to enable CORS for all routes in this blueprint

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
        photo_descriptions = []
        photo_info = []

        for photo in photos:
            if photo and allowed_file(photo.filename):
                filename, file_path = save_file(photo)  # Unpack both returned values
                
                description = extract_text_from_image(file_path)  # Pass only the file_path
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