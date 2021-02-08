#!/usr/bin/python3

import os
import time
from glob import glob
import configparser
import shutil
import soundfile as sf


config = configparser.ConfigParser()
config.read('/home/pi/soft_raspberry/config.ini')

SEACH_DIR = config['default']['dir_search']
SAVE_DIR = config['default']['dir_save']
RES_DIR = config['default']['dir_result']
SIZE = int(config['default']['size'])


def split_audio(fname):
    data, sr = sf.read(SAVE_DIR + fname)

    for counter in range(len(data) // sr // SIZE + 2):
        start = counter * SIZE * sr
        end = start + (SIZE * sr)
        part_data = data[start:end]
        sf.write(f'{RES_DIR}{counter}-{fname}.wav', part_data, sr)


def moving_files():
    lst_faudio = []
    for fpath in glob(SEACH_DIR + '**/*.wav'):
        if fpath in os.listdir(RES_DIR):
            continue
        lst_faudio.append(RES_DIR + fpath.split('/')[-1])
        size_file_0 = os.path.getsize(fpath)
        shutil.copy2(fpath, SAVE_DIR)
        size_file_1 = os.path.getsize(SAVE_DIR + fpath.split('/')[-1])
        if size_file_0 == size_file_1:
            os.rename(SAVE_DIR + fpath.split('/')[-1], RES_DIR + fpath.split('/')[-1])
            split_audio(fpath.split('/')[-1])
            os.remove(fpath)
        else:
            os.remove(SAVE_DIR + fpath.split('/')[-1])
    return lst_faudio


def main_loop():
    while True:
        try:
            moving_files()
        except:
            print('Error')
        time.sleep(5)


if __name__ == '__main__':
    split_audio('test.wav')
