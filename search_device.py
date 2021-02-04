import os
import time
from glob import glob
from treatment_dir import search_file

SEACH_DIR = 'D:/Project/soft_raspberry/raw/'
SAVE_DIR = 'save/'


def moving_files(path):
    for fpath in glob(SEACH_DIR + path + '/*.wav'):
        os.system(f'mv {fpath} {SAVE_DIR}')
        print(f'mv {fpath} {SAVE_DIR}')


def main_loop():
    start_dir = os.listdir(SEACH_DIR)

    while True:
        now_dir = os.listdir(SEACH_DIR)
        if start_dir != now_dir:
            # print('NEW')
            [moving_files(object_dir) for object_dir in now_dir if not object_dir in start_dir]
            search_file()
            start_dir = now_dir
        # else:
            # print('OK')
        time.sleep(5)


if __name__ == '__main__':
    main_loop()