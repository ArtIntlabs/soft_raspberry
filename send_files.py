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


def get_file_timing(file):
    timing = file.split('_')[3]
    return f'{timing[:2]}:{timing[2:4]}:{timing[4:6]}'


def get_file_date(file):
    date = file.split('_')[2]
    return f'{date[6:8]}.{date[4:6]}.{date[:4]}'


def send_file(file, session_id):
    mac_address = 'b8:27:eb:af:a1:00'
    # mac_address = get_mac_address()
    while not internet_on():
        continue
    request = {'stationMac': mac_address, 'audioFile': encode_file(file).decode('utf-8'), 'time': get_file_timing(file),
               'data': get_file_date(file), 'sessionId': session_id, 'microType': '0'}
    response = requests.post(ADD_AUDIO_INFO_URL, json=request)

    while response.status_code != requests.codes.OK:
        response = requests.post(ADD_AUDIO_INFO_URL, json=request)


def main(args):
    while True:
        with open(LOG_FILE, 'w') as f:
            time_started = time.time()
            session_id = start_session()
            f.write('Got session id\n')
            while time_started - time.time() < 24 * 60 * 60:
                current_files = os.listdir(args['dir_result'])
                f.write(f'Seeing files {current_files} at dir {args["dir_result"]}\n')
                for file in current_files:
                    send_file(args['dir_result'] + file, session_id)
                    f.write(f'Sent file {file}\n')
                    os.remove(args['dir_result'] + file)
                    f.write(f'Deleted file {file}\n')
                time.sleep(50)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config.ini')
    main(config['default'])
