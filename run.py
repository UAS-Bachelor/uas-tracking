from configobj import ConfigObj
import os
import socket
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE, PIPE

SERVICES_DIR = 'services/'
SERVICES_CONFIG = 'services.ini'


def load_dependencies():
    config = ConfigObj(SERVICES_CONFIG)
    for section in config:
        launch_service(section, config[section]['host'], config[section]['port'])


def launch_service(service, host, port):
    print('Checking {} service...'.format(service))
    response = check_port(host, int(port))
    if response != 0:
        print("{} service is not running, starting service at port {}".format(service, port))
        Popen([executable, SERVICES_DIR + service + '/' + service + '.py'], creationflags=CREATE_NEW_CONSOLE)
        #Popen([executable, SERVICES_DIR + service + '/' + service + '.py'], shell=True)
        #Popen([executable, SERVICES_DIR + service + '/' + service + '.py'], stdout=PIPE)
    else:
        print("{} service is already running at port {} ".format(service, port))


def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock.connect_ex((host, port))


if __name__ == '__main__':
    load_dependencies()
