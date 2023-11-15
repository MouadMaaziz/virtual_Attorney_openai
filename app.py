# app.py
import os
from flask import Flask, render_template, request, jsonify, session, make_response
from chat import chatbot, open_file, generate_intake_notes, generate_lawyers_report, generate_scenarios_and_outcomes, prepare_for_form_requirements
import openai
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_KEY')
app.secret_key = 'jet39DH-313@'

conversation = []
conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
all_messages = []


@app.route('/')
def home():
    # Clear the conversation and all_messages when visiting the home page
    if 'conversation' in session:
        session.pop('conversation', None)
    if 'all_messages' in session:
        session.pop('all_messages', None)
    return render_template('index.html')
    

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'conversation' not in session:
        session['conversation'] = conversation 
    if 'all_messages' not in session:
        session['all_messages'] = []

    # Access cookies from the request
    conversation_cookie = request.cookies.get('conversation_data')
    all_messages_cookie = request.cookies.get('all_messages_data')

    if all_messages_cookie:
        session['all_messages'] = json.loads(all_messages_cookie)
    if conversation_cookie:
        session['conversation'] = json.loads(conversation_cookie)

    # Intake portion
    while True:
        # get user input
        text = request.args.get('user-input', '')
        if text == 'DONE' or text == '' :
            break
        
        session['all_messages'].append(f'CLIENT: {text}')
        #store the user's message and the Lawyer's response:
        session['conversation'].append({'role': 'user', 'content': text})
        response_text, tokens = chatbot(session['conversation'])
        session['conversation'].append({'role': 'assistant', 'content': response_text})  
        
        session['all_messages'].append(f'INTAKE: {response_text}') 
        response = make_response(jsonify({'text': response_text}))
        response.set_cookie('conversation_data', json.dumps(session['conversation']), httponly=False)
        response.set_cookie('all_messages_data', json.dumps(session['all_messages']), httponly=False)
        return response


    # Generate intake notes
    notes = generate_intake_notes(session['all_messages'])

    result = request.args.get('results', '')

    if result =='report':
        report = generate_lawyers_report(notes)
        return jsonify({'lawyer_report': report})
    
    elif result =='form':
        form = prepare_for_form_requirements(notes)
        return jsonify({'form_requirements': form})
    
    elif result =='scenarios':
        scenario = generate_scenarios_and_outcomes(notes)
        return jsonify({'scenario_and_outcomes':scenario})

    
    return jsonify({'notes': notes })



if __name__ == '__main__':
    openai.api_key = os.getenv('OPENAI_KEY')
    app.run(debug=True)


