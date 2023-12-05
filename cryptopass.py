import PySimpleGUI as sg
import string
import random
import json
from cryptography.fernet import Fernet
import os
from tkinter import filedialog

sg.theme("SystemDefault") 

settings_location = 'settings.json'
locations = {"key_location" : " ", "password_location" : " "}

''' select the backed up files when clicked on the backed up selecting_backedup_new function '''
def selecting_backup():
    key_location = sg.popup_get_file(title="Select Key Location", message="Enter Location to Key",  default_path=None, icon='icon/systemlockscreen_94256.ico')
    if key_location.endswith(".key"):
        sg.popup("File Loaded Successfully", icon='icon/systemlockscreen_94256.ico')
    else:
        sg.popup("File Not Found Error", icon='icon/systemlockscreen_94256.ico')
        return selecting_backup()
    
    password_location = sg.popup_get_file(title="Select Password List Location", message="Enter Location to Password File",  default_path=None, icon='icon/systemlockscreen_94256.ico')
    if password_location.endswith(".json"):
        sg.popup("Password file Loaded", icon='icon/systemlockscreen_94256.ico')
    else:
        sg.popup("File Not Found Error", icon='icon/systemlockscreen_94256.ico')
        return selecting_backup()
    
    settings_file = {"key_location": f"{key_location}", "password_location": f"{password_location}"}
    with open(settings_location, 'w') as settings_file_writing:
        json.dump(settings_file, settings_file_writing)
    locations.update(settings_file)
    
''' selecting_backedup_new function starts fresh file '''
def first_start_create():
    sg.popup("Enter Location to store Key",  icon='icon/systemlockscreen_94256.ico')
    key_location = filedialog.askdirectory(initialdir=os.listdir())
    sg.popup(f"{key_location}.key", icon='icon/systemlockscreen_94256.ico')

    key = Fernet.generate_key()
    with open(f"{key_location}/keyfile.key", 'wb') as keyfile:
        keyfile.write(key)
    sg.popup("Enter Location to store Password File", icon='icon/systemlockscreen_94256.ico')

    password_location = filedialog.askdirectory(initialdir=os.listdir())
    settings_file = {"key_location": f"{key_location}/keyfile.key", "password_location": f"{password_location}/password.json"}
    with open(settings_location, 'w') as settings_file_writing:
        json.dump(settings_file, settings_file_writing)

''' to select backup file or first time to start running '''
def selecting_backup_new():
    yes_text = "Backup"
    no_text = "New"
    layout = [
        [sg.Text("First Run Do you Have Backed Up Files? or Create New Files?")],
        [sg.Button(yes_text), sg.Button(no_text)]
    ]
    window = sg.Window("No Files Found", layout, icon='icon/systemlockscreen_94256.ico')
    event, _ = window.read()
    if event == yes_text:
        window.close()
        selecting_backup()
    elif event == no_text:
        window.close()
        first_start_create()
    else:
        window.close()

''' generating the password on generate button press '''
def GenPassword(password_length ,specialCharater, numbers, upperCase, lowerCase):
    letters = string.ascii_letters
    digi = string.digits
    chara = string.punctuation
    password = []
    userPasswordLength = int(password_length)
    pool = ""
    if specialCharater:
        pool += chara
    if numbers:
        pool += digi
    if upperCase:
        pool += string.ascii_uppercase
    if lowerCase:
        pool += string.ascii_lowercase
    for i in range(userPasswordLength):
        randomchar = random.choice(pool) 
        password.append(randomchar)
    return ''.join(password)

''' saving the generated password to the file '''
def saving_password(siteName, password):
    with open(settings_location, 'r') as settings_file:
        settings = json.load(settings_file)
    selected_key_location = settings['key_location']
    selected_password_location = settings['password_location']

    with open(f"{selected_key_location}", 'rb') as filekey:
        key = filekey.read()
    fernet = Fernet(key)

    try:
        with open(f"{selected_password_location}", 'rb') as enc_file:
            encrypted = enc_file.read()
        decrypted = fernet.decrypt(encrypted)
        decoded_data = decrypted.decode('utf-8')
        json_data = json.loads(decoded_data)
    except FileNotFoundError:
        json_data = {}
    if siteName in json_data:
        sg.Popup(f"{siteName} already exists in the password file.", icon="icon/systemlockscreen_94256.ico")
        return  # Do not proceed with saving
    
    json_data[siteName] = password
    encoded_data = json.dumps(json_data).encode('utf-8')
    encrypted = fernet.encrypt(encoded_data)
    with open(f"{selected_password_location}", 'wb') as enc_file:
        enc_file.write(encrypted)
    sg.Popup(f'Password Saved in {os.getcwd()}', icon='icon/systemlockscreen_94256.ico')
    
''' shows the saved password when searched up '''
def showing_password(search_website):
    with open(settings_location, 'r') as settings_file:
        settings = json.load(settings_file)
    selected_key_location = settings['key_location']
    selected_password_location = settings['password_location']

    with open(f"{selected_key_location}", 'rb') as filekey:
        key = filekey.read()
    fernet = Fernet(key)

    with open(f"{selected_password_location}", 'rb') as enc_file:
        encrypted = enc_file.read()
    decrypted = fernet.decrypt(encrypted)
    decoded_data = decrypted.decode('utf-8')
    password_data = json.loads(decoded_data)
    websites_found = []

    if search_website in password_data:
        websites_found.append(f"{password_data[search_website]}")
    if websites_found:
        window['saved_password'].update("\n".join(websites_found))
    else:
        window['saved_password'].update("No Website Found")
    encoded_data = json.dumps(password_data).encode('utf-8')
    encrypted = fernet.encrypt(encoded_data)
    with open(f"{selected_password_location}", 'wb') as enc_file:
        enc_file.write(encrypted)

''' Generating the Layout for Generating the password '''
def gen_layout():
    gen_layout_frame = [
        [sg.Text("Site Name", font=("Arial", 10, 'bold'))],
        [sg.Input(key='siteName')],
        [sg.Checkbox("Special Characters", default=False, font=("Arial", 10, 'bold'), key='sCharacter'), sg.Checkbox("Numbers", default=False, font=("Arial", 10, 'bold'), key='numbers')],
        [sg.Checkbox("Upper Case", default=False, font=("Arial", 10, 'bold'), key='uCharater'), sg.Checkbox("Lower Case", default=False, font=("Arial", 10, 'bold'), key='lCharater')],
        [sg.Text("Length Of Password", font=("Arial", 10, 'bold'))],
        [sg.Input(key='lengthOfPassword', size=(5, 10)), sg.Button("Generate Password", key='gen', expand_x=True, font=("Arial", 10, 'bold'))],
    ]
    return gen_layout_frame

''' Generating the layout for the resulted of the Password '''
def resulted_password(): 
    resulted_frame = [
        [sg.Input(key='resulted_password', expand_x=True)],
        [sg.Button("Save Password", key='save', expand_x=True, font=("Arial", 10, 'bold'))]
    ]
    return resulted_frame

''' Generating the layout for the showing the Password '''
def show_passwords():
    show_password_layout = [
        [sg.Text("Enter Site Name", font=("Arial", 10, 'bold'))],
        [sg.Input(key='search_website')],
        [sg.Button("Search Passwords", key='search', expand_x=True, font=("Arial", 10, 'bold'))],
        [sg.Input(key='saved_password')],
    ]
    return show_password_layout

geni_result = [
    [sg.Frame("Generated Password", layout=resulted_password(), font=("Arial", 10, 'bold'), title_color='Red'),],
    [sg.Frame("Search Password", layout=show_passwords(), font=("Arial", 10, 'bold'), title_color='Red')]
]

''' Generating the main layout for the program '''
layout = [
    [sg.Frame("Password Configuration", layout=gen_layout(), font=("Arial", 10, 'bold'), expand_y=True, title_color='Red'), sg.Frame("", layout=geni_result, title_color='red' ,key='show', expand_y=True, font=("Arial", 10, 'bold'))], 
]

window = sg.Window("CryptoPass", layout, font=("Arial", 10, 'bold'), icon='icon/systemlockscreen_94256.ico')

if __name__ == '__main__':
    ''' runs the first check to see if settings file is available '''
    if os.path.isfile(settings_location):
        pass
    elif FileNotFoundError:
        selecting_backup_new()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'gen':
            ''' getting the values for the required passwords '''
            password_length = values['lengthOfPassword']
            specialCharater = values['sCharacter']
            numbers = values['numbers']
            upperCase = values['uCharater']
            lowerCase = values['lCharater']
            GenPassword(password_length, specialCharater, numbers, upperCase, lowerCase)
            window['resulted_password'].update(GenPassword(password_length=password_length, 
            specialCharater=specialCharater, numbers=numbers, upperCase=upperCase, lowerCase=lowerCase))
        if event == 'save':
            siteName = values['siteName']
            password = values['resulted_password']
            saving_password(siteName, password)
        if event == 'search':
            search_website = values['search_website']
            showing_password(search_website)

    window.close()
