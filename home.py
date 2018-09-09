import os
import dweepy
import datetime
import wakeonlan
import traceback
import panasonic_viera
import logging
import socket
import subprocess
import random
import argparse
import signal

logger = logging.getLogger('Home')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('{}.log'.format(socket.gethostname()))
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
rc = None
logger.addHandler(fh)
maclist = {
"Minolispc":"30:9C:23:0D:E4:80",
"pi":"B8:27:EB:BC:6F:21",
"galaxy":"10:30:47:EA:7A:55",
"spc":"D8:CB:8A:C1:54:85",
"Anubis":"B8:E8:56:6C:3A:E1",
"shield":"00:04:4B:72:8C:F0",
"worklaptop":"A0:B3:CC:46:D4:01",
"bedtv": "CC:7E:E7:D1:5C:49",
"iphone": "6C:AB:31:38:68:23"
}

hostlist = {
"mpc":"DESKTOP-CS182H9",
"pi":"piAlarm",
"galaxy":"Samsung(android)",
"spc":"StephenGamePC",
"Anubis":"Anubis",
"shield":"NVIDIA(android)",
"worklaptop":"worklaptop-PC",
"bedtv": "COM-MID1",
"iphone": "Rudiger"
}

iplist = {}

myip = socket.gethostbyname(socket.gethostname())

logger.info("Welcome to house control")
logger.info("Started at: " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
logger.info("Running on host {} with ip {}".format(socket.gethostname(), myip))

def client_listen():
    logger.info("Starting client listener")
    while True:
        try:
            for dweep in dweepy.listen_for_dweets_from('sgsmcpi'):
                logger.info("Dweep received:\n{}".format(dweep))
                for key in dweep["content"]:
                    if key == "goodnight":
                        shutdown()
        except:
            print(traceback.format_exc(1))

def listen():
    logger.info("Time to get the IPs for the different devices")
    ipscan()
    counter = 0
    try:
        rc = panasonic_viera.RemoteControl(iplist["bedtv"])
    except:
        logger.warning("Error initializing TV remote:\n{}".format(traceback.format_exc()))
    logger.info("Starting listener")
    while True:
        try:
            if counter > 0:
                if check_play() == False:
                    counter -= 1
                    play_random()
        except:
            print(traceback.format_exc(1))
        try:
            for dweep in dweepy.listen_for_dweets_from('sgsmcpi', 15):
                logger.info("Dweep received:\n{}".format(dweep))
                for key in dweep["content"].keys():
                    logger.info("Processing key {}".format(key))
                    if key == 'volume_up':
                        volume_up()
                    elif key == "volume_down":
                        volume_down()
                    elif key == "volume_down":
                        volume_down()
                    elif key == "play":
                        counter = 8
                        play_random()
                    elif key == "stop_play":
                        counter = 0
                        kill_mp3()
                    elif key == "wake_pc":
                        logger.info("Running wake_pc")
                        wake_pc(maclist['spc'])
                    elif key == "minoli_pc":
                        wake_pc(maclist['Minolispc'])
                    elif key == "bedtime":
                        shield_on()
                    elif key == "goodnight":
                        tv_off()
                    elif key == "wah":
                        wake_pc(maclist['worklaptop'])
        except:
            print(traceback.format_exc(1))


def shutdown():
    subprocess.call('shutdown /f /sg', shell=True)


def init_remote():
    rc = panasonic_viera.RemoteControl(iplist["bedtv"])

def wake_pc(ip):
    logger.info("Starting Wake PC for {}".format(ip))
    wakeonlan.send_magic_packet(ip)

def volume_up(amount=3):
    current_volume = rc.get_volume()
    rc.set_volume(current_volume + amount)

def tv_off():
    panasonic_viera.RemoteControl.turn_off()

def volume_down(amount=-3):
    current_volume = rc.get_volume()
    rc.set_volume(current_volume + amount)

def shield_on():
    logger.info("Turning on shield")


def ipscan():
    logger.info("IP Scan initiated. Current ip list has {} items:\n{}".format(len(iplist), iplist))
    for key in hostlist.keys():
        try:
            logger.info("Getting ip address for host key {} - hostname {}".format(key, hostlist[key]))
            iplist[key] = socket.gethostbyname(hostlist[key])
            logger.info("IP added: {}".format(iplist[key]))
        except:
            logger.warning("Error getting ip address for host key: {} - hostnane {}\n{}".format(key, hostlist[key], traceback.format_exc()))
    logger.info("iplist now has {} items\n".format(len(iplist), iplist))


parser = argparse.ArgumentParser()
parser.add_argument('--client', default="false" )
args = parser.parse_args()
print (args.client)




lovelineMp3s = []
for dir, subdirs, files in os.walk('/home/pi/Music/LoveLine'):
    for file in files:
        lovelineMp3s.append(dir + '/' + file)

subp = None

for line in lovelineMp3s:
    print line


def play_random():
    file = lovelineMp3s[random.randint(0, len(lovelineMp3s))]
    print( 'Playing Loveline file: ' +file)
    subp = subprocess.Popen(['mpg123', '-q', file])

def kill_mp3():
    counter = 0
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if 'mpg123' in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

def check_play():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    found = False
    for line in out.splitlines():
        if 'mpg123' in line:
            found = True

    return found



if args.client=="true":
    client_listen()
else:
    print('listen()')
    listen()


