#!/usr/bin/python3
import configparser
import json
import os
import time
import urllib
from base64 import b64encode
from urllib.error import URLError

import requests

# from getmac import get_mac_address


config = configparser.ConfigParser()

LOG_FILE = './log.log'

if not os.path.exists(LOG_FILE):
    os.mknod(LOG_FILE)

SERVER_URL = 'https://bk.tell2sell.ru'
ADD_START_RECORDING_URL = SERVER_URL + '/api/services/app/AudioRecord/AddStartRecording'
ADD_AUDIO_INFO_URL = SERVER_URL + '/api/services/app/AudioRecord/AddAudioInfo'


def internet_on():
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except URLError:
        return False


def start_session():
    mac_address = 'b8:27:eb:af:a1:00'
    # mac_address = get_mac_address()
    request = {'stationMac': mac_address}
    while not internet_on():
        continue
    response = requests.post(ADD_START_RECORDING_URL, json=request)
    while response.status_code != requests.codes.OK:
        response = requests.post(ADD_START_RECORDING_URL, params=request)
    content = json.loads(response.content)
    return content['result']['sessionId']


def encode_file(file):
    with open(file, 'rb') as f:
        encoded = b64encode(f.read())
    return encoded


def get_date_time(file):
    date = get_file_date(file)
    timing = get_file_timing(file)
    timing += '.0000Z'
    return date + 'T' + timing


def get_file_timing(file):
    timing = file.split('_')[3]
    return f'{timing[:2]}:{timing[2:4]}:{timing[4:6]}'


def get_file_date(file):
    date = file.split('_')[2]
    day = date[6:8]
    month = date[4:6]
    year = date[:4]
    # return f'{date[6:8]}.{date[4:6]}.{date[:4]}'
    return f'{year}-{month}-{day}'

def send_file(file, session_id):
    mac_address = 'b8:27:eb:af:a1:00'
    # mac_address = get_mac_address()
    while not internet_on():
        continue
    request = {'stationMac': mac_address, 'audioFile': encode_file(file).decode('utf-8'),
               'startTime': get_date_time(file), 'sessionId': session_id, 'microType': 0}
    response = requests.post(ADD_AUDIO_INFO_URL, json=request)

    while response.status_code != requests.codes.OK:
        response = requests.post(ADD_AUDIO_INFO_URL, json=request)


def main(args):
    with open(LOG_FILE, 'w') as f:
        pass
    while True:
        time_started = time.time()
        session_id = start_session()
        with open(LOG_FILE, 'a') as f:
            f.write(f'Got session id {session_id}\n')
        while time_started - time.time() < 24 * 60 * 60:
            current_files = os.listdir(args['dir_result'])
            with open(LOG_FILE, 'a') as f:
                f.write(f'Seeing files {current_files} at dir {args["dir_result"]}\n')
            for file in current_files:
                send_file(args['dir_result'] + file, session_id)
                with open(LOG_FILE, 'a') as f:
                    f.write(f'Sent file {file}\n')
                os.remove(args['dir_result'] + file)
                with open(LOG_FILE, 'a') as f:
                    f.write(f'Deleted file {file}\n')
            time.sleep(50)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config.ini')
    main(config['default'])
