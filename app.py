import os
from flask import Flask, render_template, request, jsonify, session
from chat import (chatbot, open_file, generate_intake_notes, generate_lawyers_report,
                  generate_scenarios_and_outcomes, prepare_for_form_requirements,
                  )

from dotenv import load_dotenv
import datetime
from pathlib import Path

load_dotenv()
PROJECT_PATH = Path.cwd()
LOG_FOLDER = PROJECT_PATH.joinpath('logs')
 

app = Flask(__name__)

conversation = []
all_messages = []
app.secret_key = 'jet39DH-313@'


@app.route('/')
def home():
    # Every time the page is refreshed, any cached conversation 
    # should be wwiped out.
    if 'conversation' in session:
        session.pop('conversation', None)
    if 'all_messages' in session:
        session.pop('all_messages', None)
    if 'notes_file' in session:
        session.pop('notes_file', None)
    return render_template('index.html')
    

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    ''' This endpoint is meant to be responding to AJAX requestes (Q&A)
    '''
    # Each time we need to load the latest conversation. if it's 
    # the first time, just initiate the system prompt.
    conversation = session.get('conversation', 
                               [{'role': 'system',
                                 'content': open_file('system_01_intake.md')
                                 }])
    all_messages = session.get('all_messages', [])
    
    
    # Keep the conversation going as long as the user doesn't 
    # enter DONE or an empty string: 
    while True:
        # get user input
        text = request.args.get('user-input', '')
        
        if text == 'DONE' or text == '' :
            break
        
        #store the user's message :
        all_messages.append(f'CLIENT: {text}')
        conversation.append({'role': 'user', 'content': text})
        
        # Get the Lawyer's response:
        response_text, tokens = chatbot(conversation)
        
        # Store the Lawyer's response:
        conversation.append({'role': 'assistant', 'content': response_text})  
        all_messages.append(f'INTAKE: {response_text}')

        # Update session data after each iteration
        session['conversation'] = conversation
        session['all_messages'] = all_messages
         
        return jsonify({'text': response_text})

    # When the user types DONE, Laywer's notes are generated
    notes_file = session.get('notes_file', None)
    if not notes_file:
        notes, notes_file = generate_intake_notes(all_messages)
        session['notes_file'] = notes_file
        print('created note_file')
    notes = open_file(session['notes_file'])
    
    # The user's requests after the conversation, it can be any of the following:    
    # A report of his legal case, The required documents, a court simulation,
    # or he could proceed directly to court by getting personal attourny.
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
    
    elif result =='court':
        report = generate_lawyers_report(notes)
        
        conversation = [{'role': 'system', 'content': open_file('system_01_questionning_bot.md')}]
        all_messages = []
        
        # Storing the user's message
        all_messages.append(f'CLIENT: {notes}\n{report}')
        conversation.append({'role': 'user', 'content': report})
        
        # Getting the assistant's message
        response_text, tokens = chatbot(conversation, max_tokens= 500)
        
        # Stroting the assistant's message
        conversation.append({'role': 'assistant', 'content': response_text})  
        all_messages.append(f'INTAKE: {response_text}')
        
        # Update session data after with the new personal attorney chat:
        session['conversation'] = conversation
        session['all_messages'] = all_messages
        
        return jsonify({'text': response_text})

    return jsonify({'notes': notes })



@app.teardown_request
def cleanup_upload_folder(request):
    file_list = os.listdir(LOG_FOLDER)
    threshold_date = datetime.datetime.now() - datetime.timedelta(hours=2)
    print(file_list)
    for file in file_list:
        file_path = LOG_FOLDER.joinpath(file)
        file_stat = os.stat(file_path)
        file_mtime = datetime.datetime.fromtimestamp(file_stat.st_mtime)
        if file_mtime < threshold_date and str(file_path).endswith(('.txt')):
            os.remove(file_path)
            print(f"Removed {file_path}")



if __name__ == '__main__':
    app.run(debug=True)


