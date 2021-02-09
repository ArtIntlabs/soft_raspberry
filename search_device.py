#!/usr/bin/python3

import os
import time
from glob import glob
import configparser
import shutil
import wave
import pyaudio


config = configparser.ConfigParser()
config.read('/home/pi/soft_raspberry/config.ini')

SEACH_DIR = config['default']['dir_search']
SAVE_DIR = config['default']['dir_save']
RES_DIR = config['default']['dir_result']

SIZE = int(config['audio']['size'])
SR = int(config['audio']['sr'])
CHANNELS = int(config['audio']['channels'])


def split_audio_2(fname):
    wf = wave.open(SAVE_DIR + fname, 'rb')
    p = pyaudio.PyAudio()
    counter = 0
    while True:
        data = wf.readframes(SIZE * SR)
        if len(data) == 0:
            break

        waveFile = wave.open(f'{RES_DIR}{counter}-{fname}', 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        waveFile.setframerate(SR)
        waveFile.writeframes(data)
        waveFile.close()
        del data

        counter += 1


def moving_files():
    lst_faudio = []
    list_file_device = glob(SEACH_DIR + '**/*.wav')
    list_file_pc = glob(SAVE_DIR + '*.wav')
    list_file = list_file_pc + list_file_device
    for fpath in list_file:
        if fpath in os.listdir(RES_DIR):
            if fpath.split('/')[-1] in os.listdir(SEACH_DIR):
                split_audio_2(fpath.split('/')[-1])
                os.remove(SAVE_DIR + fpath.split('/')[-1])
            continue
        lst_faudio.append(RES_DIR + fpath.split('/')[-1])
        size_file_0 = os.path.getsize(fpath)
        if os.path.exists(SAVE_DIR + fpath.split('/')[-1]):
            size_file_1 = os.path.getsize(SAVE_DIR + fpath.split('/')[-1])
            if size_file_0 != size_file_1:
                os.remove(SAVE_DIR + fpath.split('/')[-1])
                shutil.copy2(fpath, SAVE_DIR)
        else:
            shutil.copy2(fpath, SAVE_DIR)
        size_file_1 = os.path.getsize(SAVE_DIR + fpath.split('/')[-1])
        if size_file_0 == size_file_1:
            split_audio_2(fpath.split('/')[-1])
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
    main_loop()
