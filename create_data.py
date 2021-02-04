from pynput.keyboard import Key, Listener
import matplotlib.pyplot as plt
import concurrent.futures
import numpy as np
import subprocess
from datetime import datetime, time, timedelta
import pyaudio
import wave
import sys
import os

OPEN = False

def stop(key):
    global OPEN
    if key == Key.esc:
        OPEN = True
        print('Stop')
        return False

def convert(seconds): 
    min, sec = divmod(seconds, 60) 
    hour, min = divmod(min, 60) 
    return "%d:%02d:%02d" % (hour, min, sec) 

def to_td(h):
    ho, mi, se = h.split(':')
    return timedelta(hours=int(ho), minutes=int(mi), seconds=int(se))


class AudioRecorder:
    def __init__(self, device, path=None, path_dir='data'):
        self.path_dir = path_dir
        self.path = path
        if self.path:
            self.data = self.path.split('_')[-4]
            self.year = self.data[:4]
            self.month = self.data[4:6]
            self.day = self.data[6:]

            self.time = self.path.split('_')[-3]
            self.hour = int(self.time[:2])
            self.minute = int(self.time[2:4])
            self.second = int(self.time[4:])
            self.time_start_rec = f'{self.hour}:{self.minute}:{self.second}'

            self.time_start = timedelta(hours=self.hour, minutes=self.minute)

            self.id_device = self.path.split('_')[-1][:-4]


        self.open = True
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.p = pyaudio.PyAudio()
        if path:
            # self.process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
            #                                  self.path,
            #                                  '-ar', str(self.rate), '-ac', str(self.channels), '-f', 's16le', '-'],
            #                                 stdout=subprocess.PIPE)
            self.wf = wave.open(self.path, 'rb')
        else:
            self.frames_per_buffer = 4000
            self.input_device = device
            self.stream = self.p.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.audio_frames = []
        self.rec = False
        self.stop_iter = 5
        self.iter_file = 0
        self.sample = 0
        self.counter = 0
        self.start = 0
        self.end = 0

    def record(self):
        print('Start')
        self.stream.start_stream()
        while self.open:
            self.data = self.stream.read(4000)
            self.value = np.abs(np.frombuffer(self.data, dtype=np.int16)).mean()
            self._detected()
            self.counter += 1
            self.is_stop()

    def _detected(self):
        if self.value > 800:
            self.start = self.counter * 4000
            self.rec = True
            self.sample += 1
            self.audio_frames.append(self.data)
            self.stop_iter = 5
        elif self.rec and self.stop_iter > 0:
            self.audio_frames.append(self.data)
            self.stop_iter -= 1
        elif self.rec and self.stop_iter <= 0 and self.sample > 20:
            self.write_file()
            self.audio_frames = []
            self.iter_file += 1
            self.rec = False
            self.sample = 0
        elif self.sample < 20  and self.stop_iter <= 0:
            self.audio_frames = []
            self.rec = False
            self.sample = 0


    def read(self):
        while self.open:
            self.data = self.wf.readframes(4000)
            # self.data = self.process.stdout.read(4000)
            if len(self.data) == 0:
                self.open = False
            self.value = np.abs(np.frombuffer(self.data, dtype=np.int16)).mean()
            self.counter += 1
            self._detected()


        

    def write_file(self):
        #print(f'{self.path_dir}/{self.iter_file}.wav')
        lenght = len(self.audio_frames)
        lenght_time = lenght * 4000 / 16000
        time_end = (self.counter * 4000) / 16000
        time_start = time_end - lenght_time

        time_fragment_start = str(sum(map(to_td, [convert(time_start), self.time_start_rec]), timedelta())).replace(':', '')
        if len(time_fragment_start) == 5:
            time_fragment_start = '0' + time_fragment_start
        time_fragment_end = str(sum(map(to_td, [convert(time_end), self.time_start_rec]), timedelta())).replace(':', '')
        if len(time_fragment_end) == 5:
            time_fragment_end = '0' + time_fragment_end

        waveFile = wave.open(f'{self.path_dir}/{time_fragment_start}-{time_fragment_end}_{self.day}-{self.month}-{self.year}_{self.id_device}.wav', 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.p.get_sample_size(self.format))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(self.audio_frames))
        waveFile.close()

    def is_stop(self):
        if OPEN:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

            # waveFile = wave.open(self.audio_filename, 'wb')
            # waveFile.setnchannels(self.channels)
            # waveFile.setsampwidth(self.p.get_sample_size(self.format))
            # waveFile.setframerate(self.rate)
            # waveFile.writeframes(b''.join(self.audio_frames))
            # print(self.audio_filename)
            # waveFile.close()


def start_audio_recording(device=0, path=None, path_dir='data'):
    if path:
        audio_thread = AudioRecorder(device, path, path_dir)
        audio_thread.read()
    else:
        audio_thread = AudioRecorder(device, path_dir)
        audio_thread.record()
    if not audio_thread.open:
        return audio_thread.audio_frames


def plot(data):
    plt.figure()
    plt.plot(data)
    plt.show()


def main(path=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        audio_0 = executor.submit(start_audio_recording, 0, path if path else None)
        if not path:
            with Listener(on_press=stop) as listener:
                listener.join()
        audio_0.result()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        main()
    else:
        main(sys.argv[1])

