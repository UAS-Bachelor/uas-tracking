from configobj import ConfigObj
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil
import time

SERVICES_DIR = 'services/'
SERVICES_CONFIG = 'services.ini'

configobj = ConfigObj(SERVICES_CONFIG)


def __launch_service(service, config):
    port = config['port']
    version = config['version']
    if 'instances' in config:
        instances = int(config['instances'])
    else:
        instances = 1

    amount_of_instances = check_port(port)
    if amount_of_instances < instances:
        instance_difference = instances - amount_of_instances
        print("Only {} instances of {} service are running, starting {} more of version {} at port {}".format(
            amount_of_instances, service, instance_difference, version, port))
        for i in range(instance_difference):
            __open_cmd(service, port, version)
    else:
        print("{} instances of {} service are already running at port {}".format(
            amount_of_instances, service, port))


def __open_cmd(service, port, version):
    Popen([executable, SERVICES_DIR + service + '/' + service + '.py',
           '-p', str(port), '-v', str(version)], creationflags=CREATE_NEW_CONSOLE)


def __close_cmd(pid):
    psutil.Process(pid).terminate()


def __upgrade_service(service, config):
    version = configobj[service]['version']
    port = config['port']
    print('Starting upgrade of {} service to version {}...'.format(
        service, version))
    amount_of_instances = check_port(port)

    count = 0
    for pid in gather_pids(port):
        count += 1
        print('Upgrading service with PID {} ({}/{})'.format(pid,
                                                             count, amount_of_instances))
        __open_cmd(service, port, version)
        __close_cmd(pid)
        time.sleep(1)


def check_port(port_to_check):
    amount_of_instances = 0
    for connection in psutil.net_connections('inet'):
        (ip, port) = connection.laddr
        if ip == '127.0.0.1' and port == int(port_to_check):
            amount_of_instances += 1
    return amount_of_instances


def gather_pids(port_to_check):
    pids = []
    for connection in psutil.net_connections('inet'):
        (ip, port) = connection.laddr
        if ip == '127.0.0.1' and port == int(port_to_check) and connection.pid != 0:
            pids.append(connection.pid)
    return pids


def run(service):
    if service in configobj:
        print('Starting {} service...'.format(service))
        __launch_service(service, configobj[service])
    elif service == 'all':
        print('Starting all services...')
        for service_section in configobj:
            __launch_service(service_section, configobj[service_section])


def upgrade(service):
    if service in configobj:
        __upgrade_service(service, configobj[service])
    elif service == 'all':
        for service_section in configobj:
            __upgrade_service(service_section, configobj[service_section])


def kill(service):
    if service in configobj:
        print('Killing {} service...'.format(service))
        port = configobj[service]['port']
        for pid in gather_pids(port):
            __close_cmd(pid)
    elif service == 'all':
        print('Killing all services...')
        for service_section in configobj:
            port = configobj[service_section]['port']
            for pid in gather_pids(port):
                __close_cmd(pid)


if __name__ == '__main__':
    while True:
        method_name, arg = input().split()
        method = locals().get(method_name)
        if not method:
            print('Method {} does not exist'.format(method_name))
        else:
            method(arg)
