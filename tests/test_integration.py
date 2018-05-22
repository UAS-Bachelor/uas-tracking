import pytest
import requests
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from services.api_gateway import api_gateway
from services.drone_information import drone_information
from scripts.util import config
from common import start_server, stop_server, __run_drone_information


@pytest.fixture
def context():
    with api_gateway.app.test_request_context():
        yield


def test_drone_information_integration(context):
    with pytest.raises(requests.exceptions.ConnectionError):
        api_gateway.get('drone_information', '/')

    server = start_server(__run_drone_information, config['drone_information']['port'])
    
    assert api_gateway.get('drone_information', '/')

    stop_server(server)


def test_different_ports_for_same_service(context):
    server_1 = start_server(__run_drone_information, config['drone_information']['port'])
    
    response = api_gateway.get('drone_information', '/')
    assert response

    stop_server(server_1)

    new_port = 6001
    server_2 = start_server(__run_drone_information, new_port)
    
    api_gateway.config = {
        'drone_information': {
            'host': '127.0.0.1', 
            'port': new_port + 1
        }
    }
    with pytest.raises(requests.exceptions.ConnectionError):
        api_gateway.get('drone_information', '/')

    api_gateway.config = {
        'drone_information': {
            'host': '127.0.0.1', 
            'port': new_port
        }
    }
    response = api_gateway.get('drone_information', '/')
    assert response

    stop_server(server_2)


if __name__ == '__main__':
    pytest.main()