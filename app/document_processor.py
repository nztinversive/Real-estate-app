import os
from werkzeug.utils import secure_filename
from PIL import Image
import base64
from openai import OpenAI
from flask import current_app

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

client = OpenAI(api_key='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')

def save_file(file):
    filename = secure_filename(file.filename)
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        raise ValueError("UPLOAD_FOLDER not configured in app")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return filename, file_path  # Return both the filename and the full file path

def extract_text_from_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail, focusing on aspects relevant to real estate."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_string}"
                        }
                    }
                ]
            }
        ]
    )
    
    return response.choices[0].message.content.strip()

def generate_tags(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates relevant tags for real estate descriptions."},
            {"role": "user", "content": f"Generate 5-10 relevant tags for this real estate description: {text}"}
        ]
    )
    
    tags = response.choices[0].message.content.strip().split(', ')
    return tags[:10]  # Ensure we return at most 10 tags

def generate_property_description(combined_description):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional real estate agent. Generate a compelling property description based on the following information."},
            {"role": "user", "content": f"Generate a property description based on this information:\n\n{combined_description}"}
        ]
    )
    
    return response.choices[0].message.content.strip()