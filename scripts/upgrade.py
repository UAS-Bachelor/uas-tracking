import argparse
import time
from util import config, open_cmd, close_cmd, check_port, gather_pids


def __upgrade_service(service, config):
    host = config['host']
    port = config['port']
    version = config['version']
    print('Starting upgrade of {} service to version {}...'.format(
        service, version))
    amount_of_instances = check_port(host, port)

    count = 0
    for pid in gather_pids(host, port):
        count += 1
        print('Upgrading service with PID {} ({}/{})'.format(pid,
                                                             count, amount_of_instances))
        open_cmd(service, host, port, version)
        close_cmd(pid)
        time.sleep(1)


def upgrade(service):
    if service in config:
        __upgrade_service(service, config[service])
    elif service == 'all':
        for service_section in config:
            __upgrade_service(service_section, config[service_section])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', metavar='service', type=str, default='all',
                        help='specify which service to upgrade')
    args = parser.parse_args()
    upgrade(args.s)
