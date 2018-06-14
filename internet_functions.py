import requests
import json
import urllib3
import time
from configparser import ConfigParser
import os


def registration():
    while True:
        local_path = os.path.dirname(os.path.abspath(__file__))
        answer = input("""
Remember to edit regconfig.ini before you start registration

1 Registration
2 Return""" + '\n')
        try:
            if answer == str('1'):
                os.system("reset")
                urllib3.disable_warnings()
                cfg2 = ConfigParser()
                cfg2.read(local_path + '/regconfig.ini')
                email = cfg2.get('Registration', 'email')
                username = cfg2.get('Registration', 'username')
                display_name = cfg2.get('Registration', 'display_name')
                password = cfg2.get('Registration', 'password')
                team = cfg2.get('Registration', 'team')
                language = cfg2.get('Registration', 'language')
                device_id = cfg2.get('Registration', 'device_id')
                device_type = cfg2.get('Registration', 'device_type')
                device_model = cfg2.get('Registration', 'device_model')
                system_version = cfg2.get('Registration', 'system_version')
                app_version = cfg2.get('Registration', 'app_version')

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
                if internet_connection():

                    request_register = requests.post('https://api.credo.science/api/v2/user/register', verify=False,
                                                     json=data_register)
                    if request_register.status_code == 200:
                        print("Registration complete. Please check your email for activation link")
                    else:
                        print(request_register.content)
                        continue
                else:
                    print("No internet connection")
            elif answer == str('2'):
                os.system("reset")
                break
        except ValueError:
            continue


def internet_connection():
    url = "http://www.google.pl"
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False


def credo_login():
    urllib3.disable_warnings()
    local_path = os.path.dirname(os.path.abspath(__file__))
    cfg = ConfigParser()
    cfg.read(local_path + '/config.ini')
    device_id = cfg.get('Detection', 'device_id')
    device_model = cfg.get('Detection', 'device_model')
    app_version = cfg.get('Detection', 'app_version')
    system_version = cfg.get('Detection', 'system_version')
    device_type = cfg.get('Detection', 'device_type')
    password = cfg.get('Detection', 'password')
    email = cfg.get('Detection', 'email')

    login = {'app_version': app_version, 'device_model': device_model,
             'device_type': device_type, 'system_version': system_version,
             'device_id': device_id, 'password': password, "email": email}

    with open("login.json", "w") as login_file:
        json.dump(login, login_file)
    with open("login.json", "r") as read_login:
        data_login = json.load(read_login)
        if internet_connection():
            request_login = requests.post('https://api.credo.science/api/v2/user/login', verify=False,
                                          json=data_login)
            return request_login.json()['token']
        else:
            print()


def old_detection_file():
    old_list = []
    cfg = ConfigParser()
    local_path = os.path.dirname(os.path.abspath(__file__))
    cfg.read(local_path + '/config.ini')
    for item in os.listdir(local_path):
        if 'old_detection' in item:
            old_list.append(item)
            for item in old_list:
                with open(item, "r") as old_read_detection:
                    old_data_detection = json.load(old_read_detection)
                    if internet_connection():
                        requests.post('https://api.credo.science/api/v2/detection',
                                      verify=False,
                                      json=old_data_detection,
                                      headers={'Authorization': 'Token %s' % credo_login()})
                        os.remove(item)
                        old_list.remove(item)


def credo_detection(detection_picture):
    local_path = os.path.dirname(os.path.abspath(__file__))
    urllib3.disable_warnings()
    cfg = ConfigParser()
    cfg.read(local_path + '/config.ini')
    latitude = cfg.get('Detection', 'latitude')
    longitude = cfg.get('Detection', 'longitude')
    altitude = cfg.get('Detection', 'altitude')
    accuracy = cfg.get('Detection', 'accuracy')
    provider = cfg.get('Detection', 'provider')
    width = cfg.get('Detection', 'width')
    height = cfg.get('Detection', 'height')
    id_detection = cfg.get('Detection', 'id_detection')
    device_id = cfg.get('Detection', 'device_id')
    androidversion = cfg.get('Detection', 'androidVersion')
    device_model = cfg.get('Detection', 'device_model')
    app_version = cfg.get('Detection', 'app_version')
    system_version = cfg.get('Detection', 'system_version')
    device_type = cfg.get('Detection', 'device_type')
    linux_time = time.time()
    linux_time_millisecond = [item for item in str(linux_time) if item != '.']
    linux_time_millisecond_format = int(''.join(linux_time_millisecond)[:13])
    detection = {"detections": [{"frame_content": detection_picture,
                                 "timestamp": '%d' % linux_time_millisecond_format,
                                 "latitude": latitude,
                                 "longitude": longitude, "altitude": altitude,
                                 "accuracy": accuracy,
                                 "provider": provider, "width": width, "height": height,
                                 "id": id_detection}],
                 "device_id": device_id, "androidVersion": androidversion,
                 "device_model": device_model,
                 "app_version": app_version,
                 "system_version": system_version, "device_type": device_type}

    with open("detection.json", "w") as detection_file:
        json.dump(detection, detection_file)
    with open("detection.json", "r") as read_detection:
        data_detection = json.load(read_detection)
    if internet_connection():
        requests.post('https://api.credo.science/api/v2/detection',
                      verify=False, json=data_detection,
                      headers={'Authorization': 'Token %s' % credo_login()})
    else:
        with open("old_detection" + str(linux_time_millisecond_format) + ".json",
                  "w") as detection_file:
            json.dump(detection, detection_file)
