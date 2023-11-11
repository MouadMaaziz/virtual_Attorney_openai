from flask import Flask, render_template, request, jsonify

import openai
from chat import chatbot, open_file, chatbot, open_file, save_file



app = Flask(__name__)

# Your existing chatbot functions and imports go here


# Read OpenAI API key from the file
openai.api_key = open_file('key_openai.txt').strip()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    conversation = data.get('conversation', [])
    response, _ = chatbot(conversation)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
