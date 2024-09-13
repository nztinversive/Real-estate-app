from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import os
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from .models import db, PropertyDescription
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

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Comment out other routes for now