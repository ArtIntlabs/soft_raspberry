import os
import time
from glob import glob
from treatment_dir import search_file
import configparser
import shutil


config = configparser.ConfigParser()
config.read('config.ini')

SEACH_DIR = config['default']['dir_search']
SAVE_DIR = config['default']['dir_save']


def moving_files(path):
    lst_faudio = []
    for fpath in glob(SEACH_DIR + path + '/*.wav'):
        # os.system(f'mv {fpath} {SAVE_DIR}')
        lst_faudio.append(SAVE_DIR + fpath.split('\\')[-1])
        shutil.copy2(fpath, SAVE_DIR)
    return lst_faudio


def main_loop():
    start_dir = os.listdir(SEACH_DIR)

    while True:
        now_dir = os.listdir(SEACH_DIR)
        if start_dir != now_dir:
            print('NEW')
            lst_faudio = [moving_files(object_dir) for object_dir in now_dir if not object_dir in start_dir]
            print(*lst_faudio)
            if lst_faudio:
                search_file(*lst_faudio)
            start_dir = now_dir
        else:
            print('OK')
        time.sleep(5)


if __name__ == '__main__':
    main_loop()