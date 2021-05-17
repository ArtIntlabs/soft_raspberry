from datetime import datetime
import pyaudio
import wave
import os

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
SIZE_WAV = 3600 # 3600
CHANNELS = 1
DIR_DATA = 'data'
SAVE_DIR = os.path.join(DIR_DATA, datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))


def save_file(filename, frames, p):
    wf = wave.open(os.path.join(SAVE_DIR, filename), 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def record():
    if not os.path.exists(DIR_DATA):
        os.mkdir(DIR_DATA)
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)

    frames = []
    counter = 0
    counter_file = 0
    size_one_file = int(RATE / CHUNK_SIZE * SIZE_WAV)
    while True:
        data = stream.read(CHUNK_SIZE)
        frames.append(data)

        if size_one_file < counter:
            save_file(f'wav-{counter_file}.wav', frames, p)
            counter_file += 1
            counter = 0
            frames = []
        counter += 1


if __name__ == '__main__':
    record()
