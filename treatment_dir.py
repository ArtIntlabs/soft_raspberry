#!/usr/bin/python3

import os
import sys
from tqdm import tqdm
from create_data import start_audio_recording
import configparser


config = configparser.ConfigParser()
config.read('./config.ini')

DIR_SAVE = config['default']['dir_result']
DIR_RAW = config['default']['dir_save']


def search_file(list_fpath) -> None:
    if not os.path.exists(DIR_SAVE): os.mkdir(DIR_SAVE)

    for path_audio in tqdm(list_fpath):
        start_audio_recording(0, path_audio)



# if __name__ == '__main__':
    # search_file()