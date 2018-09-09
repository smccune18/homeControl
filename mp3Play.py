import os
import subprocess
import random

lovelineMp3s = []
for dir, subdirs, files in os.walk('/home/pi/Music/LoveLine'):
    for file in files:
        lovelineMp3s.append(dir + '/' + file)


for line in lovelineMp3s:
    print line

def play_random(count):
    counter = 0
    while counter < count:
        counter+=1
        subprocess.Popen(['mpg123', '-q', lovelineMp3s[random.randint(0, len(lovelineMp3s))]]).wait()
        #play_mp3(random.randint(0, len(lovelineMp3s)))


