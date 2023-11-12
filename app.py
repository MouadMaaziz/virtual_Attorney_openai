# app.py
from flask import Flask, render_template, request, jsonify
from chat import chatbot, open_file, save_file, generate_intake_notes, generate_lawyers_report, generate_scenarios_and_outcomes, prepare_for_form_requirements
import openai

app = Flask(__name__)

 # text = request.args.get('user-input', '')
openai.api_key = open_file('key_openai.txt').strip()

conversation = list()
conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
user_messages = list()
all_messages = list()
print('Describe your case to the intake bot. Type DONE when done.')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
   

    # Intake portion

    while True:
        # get user input
        text = request.args.get('user-input', '') 
        if text == 'DONE':
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
    
    # Generate lawyer's report
    report = generate_lawyers_report(notes)
   
    # Prepare for form requirements
    form = prepare_for_form_requirements(notes)

    # Generate scenarios and tests
    scenario = generate_scenarios_and_outcomes(notes)

    return jsonify({'notes': notes,
                    'lawyers_report': report,
                    'form_requirements': form,
                    'scenario_and_outcomes': scenario})


if __name__ == '__main__':
    app.run(debug=True)
