# Chai AI - Desktop UI - By Victor Mattos
import os
import keyboard
import requests
import threading
import FreeSimpleGUI as fs

# Request
session = requests.session() # Session to avoid creating new requests all the time.
url = "https://api.chai-research.com/v1/chat/completions" # API link to send requests.

# Chat
MAX_HISTORY = 50 # Limit the context of the conversation. Change this so the bot remembers more (or less) of the conversation.
                 # Increasing this number means you will send more message history with each request, which may take longer.

waiting = False  # Not important for now
conversation_history = [] # Store all conversations that will be sent to the bot at once.

def main():
    # Main Window
    fs.theme('Black')
    window_size = (600, 660)
    font = ('arial', 10, 'bold')
    button_borde = 2

    layout = [
        [
            fs.Column([
                [fs.Text('CHAI AI - DESKTOP', font = ('cambria', 35, 'bold'), text_color = 'white', background_color = 'Black')]
            ],
            element_justification = 'center', expand_x = True, background_color = 'Black')
        ],
        [
            fs.Column([
                [fs.Text('Insert your API key: ', font = font), 
                 fs.Input(default_text = '', font = font, password_char = '*', background_color = 'White', text_color = 'Black', size = (25, 1), key = '-API-', justification='c'),
                 fs.Button('Connect', border_width = button_borde, font = font, size = (10, 1), key = '-CONNECT_BUTTON-', button_color = 'white on black'),
                 fs.Button('Get your API', border_width = button_borde, key = '-GET_API-', font = font, size = (16, 0), button_color = 'white on black')]
            ], element_justification = 'center', expand_x = True)
        ],
        [
            fs.Column([
                [fs.Multiline('', size = (None, 25), auto_size_text = True, font = font, disabled = True, key = '-SHOW_MESSAGES-', auto_refresh = True, background_color = 'Snow', text_color = 'Black', autoscroll = True, no_scrollbar = True)]
            ], element_justification = 'center', expand_x = True)
        ],
        [
            fs.Column([
                [fs.Multiline(default_text = 'Write here... Press \'Enter\' ou click \'Send\' button.', size = (None, 3), font = font, disabled = True, key = '-WRITE_MESSAGES-', auto_refresh = True, background_color = 'Snow', text_color = 'Black', autoscroll = True, no_scrollbar = True, enable_events = True, border_width = 2)]
            ], element_justification = 'center', expand_x = True)
        ],
        [
            fs.Column([
                [fs.Button('Restart', border_width = button_borde, font = font, size = (10, 1), key = '-RESTART-', disabled = True, button_color = 'white on black'), 
                 fs.Button('Send', border_width = button_borde, font = font, size = (10, 1), key = '-SEND-', disabled = True, button_color = 'white on black')]
            ], element_justification = 'center', expand_x = True)
        ],
        #[
        #   fs.Column([
        #        [fs.Text('Developed by V1ctor_OwneD', font = font, click_submits = True, key = '-I-')]
        #   ], element_justification = 'center', expand_x = True)
        #]
    ]

    return fs.Window(title = 'CHAI AI - Desktop Application Version 0.1 (Beta)',
                     layout = layout,
                     size = window_size,
                     finalize = True)


def connect(api = None):
    # Make a quick connection with a simple request to the API and check your response, saving the session.
    try:
        payload = {
        "model": "chai_v1",
        "messages": [
                {
                    "role": "ai",
                    "content": "."
                }
            ]
        }

        headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API_KEY": api
        }

        session.headers.update(headers)

        response = session.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            # Connected
            return True
        else:
            # Not Connected
            fs.popup('API error, please check and try again.')
            return False
    except:
        fs.popup('An error occurred while connecting the API.')


def connect_button():
    # 'Connect' button action.
    api = values['-API-']
    
    window['-API-'].update(disabled = True)
    window['-CONNECT_BUTTON-'].update('Conecting...')
    window['-CONNECT_BUTTON-'].update(disabled = True)

    status = connect(api)

    if status:
        # Connected
        window['-CONNECT_BUTTON-'].update('Connected')
        window['-SEND-'].update(disabled = False)
        window['-RESTART-'].update(disabled = False)

        window['-WRITE_MESSAGES-'].update('*I look at him from afar and approach him, still mounted on my horse.* Hello, warrior.')
        window['-WRITE_MESSAGES-'].update(disabled = False)
        window['-SHOW_MESSAGES-'].print("INFO: You are connected. The bot needs an initial context for the conversation to flow.")
        window['-SHOW_MESSAGES-'].print('-' * 139)
        window['-SHOW_MESSAGES-'].print('\n')
    else:
        # Not Connected
        window['-CONNECT_BUTTON-'].update('Connect')
        window['-CONNECT_BUTTON-'].update(disabled = False)
        window['-API-'].update(disabled = False)


def send_message(user_message = None):
    # Send a message to the bot, filter the conversation, save and return bot response.
    try:
        global conversation_history

        while len(conversation_history) >= MAX_HISTORY:
            conversation_history.pop(0)

        conversation_history.append({"role": "user", 
                                    "content": f"{user_message}"})
        payload = {
            "model": "chai_v1",
            "messages": conversation_history
        }

        # Send the message using the configured session.
        response = session.post(url, json=payload)

        if response.status_code == 200:
            # The bot received the message and responded.
            data = response.json()
            bot_response = data['choices'][0]['message']['content']
            conversation_history.append({"role": "ai", "content": bot_response})
            return bot_response
        else:
            return 'An error occurred in the bot\'s response. Try again.'
    except:
        fs.popup('An error occurred in the bot\'s response. Try again.')


def filter_text(text = None):
    parts = text.split("*")
    for i in range(1, len(parts), 2):
        parts[i] = f"\n\n*{parts[i]}*\n\n"
    return "".join(parts).strip()


def send_button():
    # 'Send' button action.
    # I decided to put all the interactions in this function to make it easier.
    global waiting
    user_message = values['-WRITE_MESSAGES-']
    filtred = filter_text(user_message)
    window['-WRITE_MESSAGES-'].update('')

    if user_message:
        # Shows the user's message.
        window['-SHOW_MESSAGES-'].print(f'{filtred}', font = ('arial', 12, 'bold'), justification = 'c')
        window['-SHOW_MESSAGES-'].print('\n')

        #window['-SHOW_MESSAGES-'].print('─' * 30)

        # Disables buttons to avoid sequential requests.
        waiting = True
        window['-SEND-'].update('Wait')
        window['-SEND-'].update(disabled = True)
        window['-RESTART-'].update(disabled = True)

        # Wait for the bot's response.
        response = send_message(user_message)
        filtred = filter_text(response)

        # Shows the bot's message.
        window['-SHOW_MESSAGES-'].print(f'{filtred}', text_color = 'black', background_color = 'white', font = ('arial', 12, 'italic'), justification = 'c')
        window['-SHOW_MESSAGES-'].print('\n')

        #window['-SHOW_MESSAGES-'].print('─' * 50)

        # Activate the buttons again.
        waiting = False
        window['-SEND-'].update('Send')
        window['-SEND-'].update(disabled = False)
        window['-RESTART-'].update(disabled = False)



def restart(window):
    # Reset message history by creating a conversation from scratch.
    global conversation_history
    conversation_history = []

    window['-SHOW_MESSAGES-'].update('') 
    window['-WRITE_MESSAGES-'].update('') 

    window['-SHOW_MESSAGES-'].print("[Chat reset successfully]", justification = 'c')
    window['-SHOW_MESSAGES-'].print('-' * 139)
    window['-SHOW_MESSAGES-'].print('\n')


# Creating the main program window
window = main()

while True:
    event, values = window.read()

    # Close program
    if event == fs.WIN_CLOSED:
        break
    
    # Connect Button
    if event == '-CONNECT_BUTTON-':
        threading.Thread(target=connect_button).start()

    # Send Button
    if event == '-SEND-':
        # Clicked on the 'Send' button.
        threading.Thread(target=send_button).start()

    # Restart Button
    if event == '-RESTART-':
        restart(window)

    # Get API Button
    if event == '-GET_API-':
        os.system('start https://docs.chai-research.com/reference/intro/getting-started')

    # Clicked on my username
    if event == '-I-':
        os.system('start https://www.reddit.com/user/V1ctor_OwneD/')

    if keyboard.is_pressed('enter') == True:
        if waiting != True:
            threading.Thread(target=send_button).start()
    
    print(event, values)

# End of program
window.close()