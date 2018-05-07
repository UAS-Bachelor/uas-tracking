import argparse
from util import config, open_cmd, check_port
from kill import kill


def __launch_service(service, config):
    #host = config['host']
    host = '0.0.0.0'
    port = config['port']
    version = config['version']
    if 'instances' in config:
        instances = int(config['instances'])
    else:
        instances = 1

    amount_of_instances = check_port(host, port)
    if amount_of_instances < instances:
        instance_difference = instances - amount_of_instances
        print("Only {} instances of {} service are running, starting {} more of version {} at {}:{}".format(
            amount_of_instances, service, instance_difference, version, host, port))
        for i in range(instance_difference):
            open_cmd(service, host, port, version)
    else:
        print("{} instances of {} service are already running at {}:{}".format(
            amount_of_instances, service, host, port))


def run(service):
    if service in config:
        print('Starting {} service...'.format(service))
        __launch_service(service, config[service])
    elif service == 'all':
        print('Starting all services...')
        for service_section in config:
            __launch_service(service_section, config[service_section])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', metavar='service', type=str, default='all',
                        help='specify which service to run')
    args = parser.parse_args()
    kill('all')
    run(args.s)
