# app.py
import os
from flask import Flask, render_template, request, jsonify
from chat import chatbot, open_file, generate_intake_notes, generate_lawyers_report, generate_scenarios_and_outcomes, prepare_for_form_requirements
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_KEY')



@app.route('/')
def home():

    return render_template('index.html')
    

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()
    # Intake portion
    while True:
        # get user input
        text = request.args.get('user-input', '')
        if text == 'DONE' or text == '' :
            break
        user_messages.append(text)
        all_messages.append(f'CLIENT: {text}')
        #store the user's message and the Lawyer's response:
        conversation.append({'role': 'user', 'content': text})
        response_text, tokens = chatbot(conversation)
        conversation.append({'role': 'assistant', 'content': response_text})  
        
        all_messages.append(f'INTAKE: {response_text}') 
        return jsonify({'text': response_text})
    

    # Generate intake notes
    notes = generate_intake_notes(all_messages)

    result = request.args.get('results', '')

    if result =='report':
        # Generate lawyer's report
        report = generate_lawyers_report(notes)
        return jsonify({'lawyer_report': report})
    
    elif result =='form':
        # Prepare for form requirements
        form = prepare_for_form_requirements(notes)
        return jsonify({'form_requirements': form})
    
    elif result =='scenarios':
        # Generate scenarios and tests
        scenario = generate_scenarios_and_outcomes(notes)
        return jsonify({'scenario_and_outcomes':scenario})

    return jsonify({'notes': notes })



if __name__ == '__main__':
    openai.api_key = os.getenv('OPENAI_KEY')
    app.run(debug=True)


