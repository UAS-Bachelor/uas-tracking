import argparse
from util import configobj, close_cmd, gather_pids


def __kill_service(service, config):
    port = configobj[service]['port']
    for pid in gather_pids(port):
        close_cmd(pid)


def kill(service):
    if service in configobj:
        print('Killing {} service...'.format(service))
        __kill_service(service, configobj[service])
    elif service == 'all':
        print('Killing all services...')
        for service_section in configobj:
            __kill_service(service_section, configobj[service_section])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', metavar='service', type=str, default='all',
                        help='specify which service to kill')
    args = parser.parse_args()
    kill(args.s)
