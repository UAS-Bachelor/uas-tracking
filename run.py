import argparse
from util import configobj, open_cmd, check_port


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
            open_cmd(service, port, version)
    else:
        print("{} instances of {} service are already running at port {}".format(
            amount_of_instances, service, port))


def run(service):
    if service in configobj:
        print('Starting {} service...'.format(service))
        __launch_service(service, configobj[service])
    elif service == 'all':
        print('Starting all services...')
        for service_section in configobj:
            __launch_service(service_section, configobj[service_section])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', metavar='service', type=str, default='all',
                        help='specify which service to run')
    args = parser.parse_args()
    run(args.s)
