from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_KEY'])

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
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a professional real estate agent. Generate a compelling property description based on the following information."},
            {"role": "user", "content": f"Generate a property description based on this information:\n\n{combined_description}"}
        ]
    )
    
    return response.choices[0].message.content.strip()