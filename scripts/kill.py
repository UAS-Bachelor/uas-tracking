import argparse
from util import config, close_cmd, gather_pids


def __kill_service(service, config):
    host = config['host']
    port = config['port']
    for pid in gather_pids(host, port):
        close_cmd(pid)


def kill(service):
    if service in config:
        print('Killing {} service...'.format(service))
        __kill_service(service, config[service])
    elif service == 'all':
        print('Killing all services...')
        for service_section in config:
            __kill_service(service_section, config[service_section])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', metavar='service', type=str, default='all',
                        help='specify which service to kill')
    args = parser.parse_args()
    kill(args.s)
