import argparse
import time
from util import configobj, open_cmd, close_cmd, check_port, gather_pids


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
        open_cmd(service, port, version)
        close_cmd(pid)
        time.sleep(1)


def upgrade(service):
    if service in configobj:
        __upgrade_service(service, configobj[service])
    elif service == 'all':
        for service_section in configobj:
            __upgrade_service(service_section, configobj[service_section])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', metavar='service', type=str, default='all',
                        help='specify which service to upgrade')
    args = parser.parse_args()
    upgrade(args.s)
