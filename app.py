# app.py
import os
from flask import Flask, render_template, request, jsonify, session, make_response
from chat import chatbot, save_file, open_file, generate_intake_notes, generate_lawyers_report, generate_scenarios_and_outcomes, prepare_for_form_requirements
import openai
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_KEY')
conversation = []
conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
all_messages = []
app.secret_key = 'jet39DH-313@'


@app.route('/')
def home():
    if 'conversation' in session:
        session.pop('conversation', None)
    if 'all_messages' in session:
        session.pop('all_messages', None)

    return render_template('index.html')
    

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    conversation = session.get('conversation', [{'role': 'system', 'content': open_file('system_01_intake.md')}])
    all_messages = session.get('all_messages', [])
    notes_file = session.get('notes_file', None)

    # Intake portion
    while True:
        # get user input
        text = request.args.get('user-input', '')
        if text == 'DONE' or text == '' :
            break
        
        all_messages.append(f'CLIENT: {text}')
        #store the user's message and the Lawyer's response:
        conversation.append({'role': 'user', 'content': text})
        response_text, tokens = chatbot(conversation)
        conversation.append({'role': 'assistant', 'content': response_text})  
        all_messages.append(f'INTAKE: {response_text}')

        # Update session data after each iteration
        session['conversation'] = conversation
        session['all_messages'] = all_messages 
        return jsonify({'text': response_text})


    # Generate intake notes
    if not notes_file:
        notes, notes_file = generate_intake_notes(all_messages)
        session['notes_file'] = notes_file
    

    result = request.args.get('results', '')
    notes = open_file(notes_file)
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




"""
Share the details of your situation with our intake bot. When you're finished, simply type 'DONE' to proceed.


Client: Hi


Assistant: Hello! Could you please describe the legal issue you're facing?

Client: my veteranian killed my dog


Assistant: I'm sorry to hear about your situation. Could you please provide more details? For instance, how did this incident occur?

Client: it was during a procedure.


Assistant: I'm sorry for your loss. Could you please provide more details about the procedure? Was it a routine procedure or a complex surgery?

Client: the veteranian let his intern do it although he has not much experience.


Assistant: I'm sorry to hear that. Can you clarify if you were informed or gave consent for the intern to perform the procedure on your dog?

Client: I didn't give consent.


Assistant: I see. Did the veterinarian or the clinic provide any explanation or reason after the incident?

Client: they lied to me about the intern experience.


Assistant: I'm sorry to hear that. Did you find out about the intern's lack of experience after the procedure? How did you discover this information?

Client: now they said the dog had little chance.


Assistant: I see. Did the veterinarian inform you about the risks and the low chances of success before the procedure?

Client: now they did not


Assistant: I understand. Did you have any written agreement or contract with the veterinarian or the clinic regarding the procedure?

Client: Yes.


Assistant: Could you please describe what the agreement or contract stated about the procedure, risks involved, and who would be performing it?

Client: I just signed that I give consent to perform the procedure on my dog. that's it.


Assistant: I see. Did the document you signed include any details about the risks of the procedure, or specify who would be performing it?

Client: DONE


NOTES

# Legal Case Notes

## Client Information:
- The client's dog was killed during a procedure performed by a veterinary clinic.

## Incident Details:
- The procedure was performed by an intern with limited experience.
- The client was not informed about the intern's lack of experience.
- The client did not give consent for the intern to perform the procedure.
- The clinic lied to the client about the intern's experience.

## Post-Incident:
- The clinic informed the client after the procedure that the dog had little chance of survival.
- The client was not informed about the risks and low chances of success before the procedure.

## Legal Documents:
- The client signed a document giving consent for the procedure to be performed on the dog.
- The document did not include any details about the risks of the procedure or specify who would be performing it.

## Potential Legal Issues:
- Lack of informed consent: The client was not informed about the intern's lack of experience and did not consent to the intern performing the procedure.
- Misrepresentation: The clinic lied about the intern's experience.
- Breach of contract: If the agreement implied that a qualified veterinarian would perform the procedure, the clinic may have breached this agreement by allowing an inexperienced intern to perform it.
- Negligence: If the intern's lack of experience and the clinic's failure to inform the client about the risks contributed to the dog's death, this could constitute negligence.




"""