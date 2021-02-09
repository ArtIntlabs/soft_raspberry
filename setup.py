from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='soft_raspberry',
    version='1.0',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=['ffmpeg', 'sox', 'pyaudio', 'portaudio19-dev'],
)