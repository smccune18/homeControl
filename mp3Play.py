import os

lovelineMp3s = []
for dir, subdirs, files in os.walk('/home/pi/Music/LoveLine'):
    for file in files:
        lovelineMp3s.append(dir + '/' + file)


for line in lovelineMp3s:
    print line


