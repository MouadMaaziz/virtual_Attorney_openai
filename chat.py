import re
import openai
from time import time
from halo import Halo
import textwrap
import yaml

# File operations

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

# API functions

def chatbot(conversation, model="gpt-4-0613", temperature=0, max_tokens=2000):
    """
    Interact with the OpenAI Chat API to generate responses in a conversation.

    Parameters:
    - conversation (list): A list of message objects representing the conversation.
                          Each message object has 'role' (str) and 'content' (str).
                          'role' can be 'system', 'user', or 'assistant'.
                          'content' contains the text of the message.
    - model (str): The OpenAI language model to use. Default is "gpt-4-0613".
    - temperature (float): Controls the randomness of the model's output.
                          Higher values make the output more random. Default is 0.
    - max_tokens (int): Limits the response to a certain number of tokens. Default is 2000.

    Returns:
    - text (str): The generated response text from the assistant.
    - total_tokens (int): The total number of tokens used in generating the response.

    This function interacts with the OpenAI Chat API to generate responses in a conversation.
    It handles potential API errors and retries the request to ensure successful communication.
    The function returns the generated response text and the total number of tokens used in the process.

    Example:
    ```
    conversation = [{'role': 'user', 'content': 'Tell me a joke.'}]
    response, tokens_used = chatbot(conversation, model="gpt-4-0613", temperature=0.7, max_tokens=1500)
    print(response)
    ```
    """
    max_retry = 7
    retry = 0
    while True:
        try:
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()

            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
            text = response['choices'][0]['message']['content']

            spinner.stop()

            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            exit(5)

def chat_print(text):
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in text.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print(f'\n\n\nCHATBOT:\n\n{formatted_text}')


def generate_intake_notes(all_messages):
    """
    Generate intake notes based on user input and save the chat log and notes to files.

    Parameters:
    - all_messages (list): List of all messages in the conversation.

    Returns:
    - notes (str): The generated notes.
    """
    print('\n\nGenerating Intake Notes')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_02_prepare_notes.md')})
    text_block = '\n\n'.join(all_messages)
    chat_log = f'<<BEGIN CLIENT INTAKE CHAT>>\n\n{text_block}\n\n<<END CLIENT INTAKE CHAT>>'
    save_file(f'logs/log_{time()}_chat.txt', chat_log)
    conversation.append({'role': 'user', 'content': chat_log})
    notes, _ = chatbot(conversation)
    print(f'\n\nNotes version of conversation:\n\n{notes}')
    save_file(f'logs/log_{time()}_notes.txt', notes)
    return notes

def generate_lawyers_report(notes):
    """
    Generate a lawyer's report based on the provided notes and save it to a file.

    Parameters:
    - notes (str): The notes from the conversation.

    Returns:
    - report (str): The generated lawyer's report.
    """
    print('\n\nGenerating Lawyer\'s Report')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_03_report.md')})
    conversation.append({'role': 'user', 'content': notes})
    report, _ = chatbot(conversation)
    save_file(f'logs/log_{time()}_report.txt', report)
    print(f'\n\nLawyer\'s Report:\n\n{report}')
    return report

def prepare_for_form_requirements(notes):
    """
    Prepare for form requirements based on the provided notes and save it to a file.

    Parameters:
    - notes (str): The notes from the conversation.

    Returns:
    - form (str): The generated form requirements.
    """
    print('\n\nPreparing for form requirements')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_04_form.md')})
    conversation.append({'role': 'user', 'content': notes})
    form, _ = chatbot(conversation)
    save_file(f'logs/log_{time()}_form.txt', form)
    print(f'\n\nForm Requirements:\n\n{form}')
    return form

def generate_scenarios_and_outcomes(notes):
    """
    Generate scenarios and outcomes based on the provided notes and save it to a file.

    Parameters:
    - notes (str): The notes from the conversation.

    Returns:
    - scenario (str): The generated scenarios and tests.
    """
    print('\n\nGenerating Scenarios and Outcomes')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_05_scenario.md')})
    conversation.append({'role': 'user', 'content': notes})
    scenario, _ = chatbot(conversation)
    save_file(f'logs/log_{time()}_scenario.txt', scenario)
    print(f'\n\nScenario and Outcomes:\n\n{scenario}')
    return scenario




def main():
    openai.api_key = open_file('key_openai.txt').strip()

    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()
    print('Describe your case to the intake bot. Type DONE when done.')

    # Intake portion

    while True:
        # get user input
        text = input('\n\nCLIENT: ').strip() # text = request.form['user_input']
        if text == 'DONE':
            break
        user_messages.append(text)
        all_messages.append(f'CLIENT: {text}')
        #store the user's message and the Lawyer's response:
        conversation.append({'role': 'user', 'content': text})
        response, tokens = chatbot(conversation)
        conversation.append({'role': 'assistant', 'content': response})  
        
        all_messages.append(f'INTAKE: {response}') # response = f'INTAKE: {response}'
        print(f'\n\nINTAKE: {response}')


     # Generate intake notes
    notes = generate_intake_notes(all_messages)

    # Generate lawyer's report
    report = generate_lawyers_report(notes)

    # Prepare for form requirements
    form = prepare_for_form_requirements(notes)

    # Generate scenarios and tests
    scenario = generate_scenarios_and_outcomes(notes)


