import speech_recognition as speech_recog
from datetime import datetime
from pydub import AudioSegment
import os
from pathlib import Path

AudioSegment.ffmpeg = os.getcwd()+"\\ffmpeg\\bin\\ffmpeg.exe"
print(AudioSegment.ffmpeg)
AudioSegment.ffmpeg = os.getcwd()+"\\ffmpeg\\bin\\ffmpeg.exe"
AudioSegment.converter = os.getcwd()+"\\ffmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = os.getcwd()+"\\ffmpeg\\bin\\ffprobe.exe"
my_file = Path(os.getcwd() + "\\file.mp3")
print ('ID1 : %s' % my_file)
audio = AudioSegment.from_mp3(my_file)