from configobj import ConfigObj
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
import time

SERVICES_DIR = 'services/'
SERVICES_CONFIG = 'services.ini'


def launch_service(service, config):
    port = config[service]['port']
    version = config[service]['version']
    if 'instances' in config[service]:
        instances = int(config[service]['instances'])
    else:
        instances = 1

    amount_of_instances = check_port(int(port))
    if amount_of_instances < instances:
        instance_difference = instances - amount_of_instances
        print("Only {} instances of {} service are running, starting {} more of version {} at port {}".format(
            amount_of_instances, service, instance_difference, version, port))
        for i in range(instance_difference):
            Popen([executable, SERVICES_DIR + service + '/' + service + '.py',
                   '-p', port, '-v', version], creationflags=CREATE_NEW_CONSOLE)
    else:
        print("{} instances of {} service are already running at port {}".format(
            amount_of_instances, service, port))


def check_port(port_to_check):
    amount_of_instances = 0
    for connection in psutil.net_connections('inet'):
        (ip, port) = connection.laddr
        if ip == '127.0.0.1' and port == port_to_check:
            amount_of_instances += 1
    return amount_of_instances


def gather_pids(port_to_check):
    pids = []
    for connection in psutil.net_connections('inet'):
        (ip, port) = connection.laddr
        if ip == '127.0.0.1' and port == port_to_check:
            pids.append(connection.pid)
    return pids


def run(service):
    config = ConfigObj(SERVICES_CONFIG)
    print('Starting {} service...'.format(service))
    if service in config:
        launch_service(service, config)
    elif service == 'all':
        for service_section in config:
            launch_service(service_section, config)


def upgrade(service):
    config = ConfigObj(SERVICES_CONFIG)
    if service in config:
        print('Starting upgrade of {} service...'.format(service))
        port = int(config[service]['port'])
        amount_of_instances = check_port(port)
        count = 0
        for pid in gather_pids(port):
            count += 1
            print('Upgrading service with PID {} ({}/{})'.format(pid,
                                                                 count, amount_of_instances))
            psutil.Process(pid).terminate()
            time.sleep(1)
            launch_service(service, config)


if __name__ == '__main__':
    while True:
        method_name, arg = input().split()
        method = locals().get(method_name)
        if not method:
            print('Method {} does not exist'.format(method_name))
        else:
            method(arg)
