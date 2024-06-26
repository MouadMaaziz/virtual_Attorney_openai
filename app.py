import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from chat import (chatbot, open_file, generate_intake_notes, generate_lawyers_report,
                  generate_scenarios_and_outcomes, prepare_for_form_requirements,
                  )
from flask_cors import CORS

from dotenv import load_dotenv
import datetime
from pathlib import Path
import time

import pandas as pd


load_dotenv()

PROJECT_PATH = Path.cwd()
LOG_FOLDER = PROJECT_PATH.joinpath('logs')


app = Flask(__name__)
CORS(app)
conversation = []
all_messages = []
app.secret_key = 'jet39DH-313@'


@app.route('/')
def home():
    # Every time the page is refreshed, any cached conversation 
    # should be wwiped out.
    clientName = session.get('userName', None)
    message = ''
    button = ''
    info = ''
    if 'userName' in session:
        print(session['userName']) # send to the template the userName
        message = f"A session under the name of {session['userName']} was found."
        button = "<button type='submit' name='cleared' value='true' form='clear-session'>Clear session</button>"    
        info = f"* Entering a different name will clear {clientName}'s session."
        
    return render_template('index.html',info = info, clientName = clientName, message = message, button = button)

@app.route('/feedback', methods=['POST', 'GET'])
def feedback_form():
    if request.method == 'POST':
        assistant_response = session['all_messages'][-1]
        rating = request.form.get('recommend')
        feedback = request.form.get('comments')
        
        row = {'assistant response': assistant_response,
               'rating': rating,
               'feedback':feedback,
               
               }
        
        try:
            df = pd.read_excel(PROJECT_PATH.joinpath('feedback.xlsx'))
            df = df._append(row, ignore_index=True)
        except FileNotFoundError as e:
            df = pd.DataFrame(row)
        
        df.to_excel(PROJECT_PATH.joinpath('feedback.xlsx'), index=False)
    return render_template('feedback_form.html')
    
    
@app.route('/get_feedback')
def get_feedback():
    return send_file(PROJECT_PATH.joinpath('feedback.xlsx'))
    
@app.route('/clear', methods=['GET'])
def clear_session():
    if request.args.get('cleared', None) == 'true':
        print('Clearing session')
        session.clear()
    return redirect(url_for('home'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    
    ''' This endpoint is meant to be responding to AJAX requestes (Q&A)
    '''
    # For debbuging:
    for k,v in request.args.items():
        print(f'{k} : {v}')
    
    # add if unserName is new (not equal to the one in session), clear session
    previous_client = session.get('userName', None)
    
    if request.args.get('userName', None) != previous_client :
        session['userName'] = request.args.get('userName', None)
        session.pop('conversation', None)
        session.pop('all_messages', None)
        session.pop('notes_file', None)
    for k, v in session.items():
        print(k, ":", v)
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
        response_text, _ = chatbot(conversation)
        
        # Store the Lawyer's response:
        conversation.append({'role': 'assistant', 'content': response_text})  
        all_messages.append(f'INTAKE: {response_text}')

        # Update session data after each iteration
        session['conversation'] = conversation
        session['all_messages'] = all_messages
         
        return jsonify({'text': response_text})

    # When the user types DONE, Laywer's notes are generated
    #notes_file = session.get('notes_file', None)
    # if not notes_file:
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
        response_text, tokens = chatbot(conversation, max_tokens= 200)
        
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


