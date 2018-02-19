from configobj import ConfigObj
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE
import psutil

SERVICES_DIR = 'services/'
SERVICES_CONFIG = 'services.ini'


def load_dependencies():
    config = ConfigObj(SERVICES_CONFIG)
    for service in config:
        launch_service(service, config)


def launch_service(service, config):
    port = config[service]['port']
    version = config[service]['version']
    if 'instances' in config[service]:
        instances = int(config[service]['instances'])
    else:
        instances = 1

    print('Checking {} service...'.format(service))
    amount_of_instances = check_port(int(port))
    if amount_of_instances < instances:
        instance_difference = instances - amount_of_instances
        print("Only {} instances of {} service are running, starting {} more at port {}".format(
            amount_of_instances, service, instance_difference, port))
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


if __name__ == '__main__':
    load_dependencies()
