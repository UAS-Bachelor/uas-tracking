from configobj import ConfigObj
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil

__services_dir = 'services/'
__services_config = 'services.ini'
configobj = ConfigObj(__services_config)


def __get_path(service):
    return __services_dir + service + '/' + service + '.py'


def open_cmd(service, host, port, version):
    Popen([executable, __get_path(service), '-a', str(host), '-p', str(port),
           '-v', str(version)], creationflags=CREATE_NEW_CONSOLE)


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
