import os
import sys
from tqdm import tqdm
from glob import glob
from create_data import start_audio_recording

DIR_SAVE = 'data/'

def search_file(path: str) -> None:
    if not os.path.exists(DIR_SAVE): os.mkdir(DIR_SAVE)

    for path_audio in tqdm(glob(path + '*.wav')):
        print(path_audio)
        start_audio_recording(0, path_audio)


if __name__ == '__main__':
    search_file(sys.argv[1])
