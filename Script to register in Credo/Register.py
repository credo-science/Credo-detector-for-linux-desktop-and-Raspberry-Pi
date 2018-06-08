import requests
import json
import urllib3
from configparser import ConfigParser
import os

local_path = os.path.dirname(os.path.abspath(__file__))

while True:
    answer = input("Enter r to start registration or h to get help")
    try:
        if answer == str('r'):
            break
        elif answer == str('h'):
            help_file = open(local_path + "/helpreg.txt", 'r')
            context = help_file.read()
            print(context)
            continue
    except ValueError:
        continue


urllib3.disable_warnings()
local_path = os.path.dirname(os.path.abspath(__file__))
cfg = ConfigParser()
cfg.read(local_path + '/registerconfig.ini')
email = cfg.get('Registraction', 'email')
username = cfg.get('Registraction', 'username')
display_name = cfg.get('Registraction', 'display_name')
password = cfg.get('Registraction', 'password')
team = cfg.get('Registraction', 'team')
language = cfg.get('Registraction', 'language')
device_id = cfg.get('Registraction', 'device_id')
device_type = cfg.get('Registraction', 'device_type')
device_model = cfg.get('Registraction', 'device_model')
system_version = cfg.get('Registraction', 'system_version')
app_version = cfg.get('Registraction', 'app_version')

register = {
  "email": email,
  "username": username,
  "display_name": display_name,
  "password": password,
  "team": team,
  "language": language,
  "device_id": device_id,
  "device_type": device_type,
  "device_model": device_model,
  "system_version": system_version,
  "app_version": app_version,
}


with open("login.json", "w") as login_file:
    json.dump(register, login_file)
with open("login.json", "r") as read_register:
    data_register = json.load(read_register)


request_login = requests.post('https://api.credo.science/api/v2/user/register', verify=False, json=data_register)
if request_login.status_code == 200:
    print("Registration complete. Please check your email for activation link")
else:
    print(request_login.content)
