import platform
import json
import psutil
import os

def __is_windows():
    return platform.system() == 'Windows'

if __is_windows():
    from sys import executable
    from subprocess import Popen, CREATE_NEW_CONSOLE
else:
    from subprocess import call


print(__file__)
print(os.path.dirname(__file__))

__services_dir = '../services/'
__services_config_file = os.path.join(os.path.dirname(__file__), '../cfg/services.json')
__environment_config_file = os.path.join(os.path.dirname(__file__), '../cfg/env_config.json')
config = json.load(open(__services_config_file))
environment_config = json.load(open(__environment_config_file))


def __get_path(service):
    return os.path.realpath(__services_dir + service + '/' + service + '.py')


def open_cmd(service, host, port, version):
    cmd = '{}'.format(__get_path(service))
    args = ['-a', str(host), '-p', str(port), '-v', str(version)]
    if environment_config['debug']:
        args.append('-d')
    if __is_windows():
        Popen([executable, cmd] + args, creationflags=CREATE_NEW_CONSOLE)
    else:
        call('python3 {} {} &'.format(cmd, ' '.join(args)), shell=True)
        #Popen('python3 {} {} &'.format(cmd, ' '.join(args)), shell=True, stdout=subprocess.PIPE)


def close_cmd(pid):
    psutil.Process(pid).terminate()


def check_port(host, port_to_check):
    amount_of_instances = 0
    for connection in psutil.net_connections('inet'):
        (ip, port) = connection.laddr
        #if ip == str(host) and port == int(port_to_check):
        if port == int(port_to_check):
            amount_of_instances += 1
    return amount_of_instances


def gather_pids(host, port_to_check):
    pids = []
    for connection in psutil.net_connections('inet'):
        (ip, port) = connection.laddr
        #if ip == str(host) and port == int(port_to_check) and connection.pid != 0:
        if port == int(port_to_check) and connection.pid != 0:
            pids.append(connection.pid)
    return pids
