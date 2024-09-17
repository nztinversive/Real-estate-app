import openai  # Ensure openai is correctly imported

# Initialize OpenAI with your API key
openai.api_key = 'your_openai_api_key_here'  # Replace with your actual API key

@main.route('/chatbot_message', methods=['POST'])
def chatbot_message():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'response': 'Please enter a message.'}), 400

    try:
        # Use OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant for a real estate investment platform. Provide helpful suggestions and summaries based on the user's data and questions."},
                {"role": "user", "content": user_message}
            ]
        )

        ai_message = response.choices[0].message['content'].strip()
        return jsonify({'response': ai_message})
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return jsonify({'response': 'Sorry, I encountered an error. Please try again later.'}), 500