import pytest
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from services.api_gateway import api_gateway
from services.drone_information import drone_information
from scripts.util import config
from common import start_server, stop_server, __run_drone_information


@pytest.fixture
def app_client():
    api_gateway.app.config['TESTING'] = True
    api_gateway.config = json.load(open(api_gateway.__services_config_file))
    app_client = api_gateway.app.test_client()
    yield app_client


def test_routes(app_client):
    response = app_client.get('/routes')
    assert response.status_code == 503
    assert response.data.decode().strip() == 'Drone information service unavailable'

    server = start_server(__run_drone_information, config['drone_information']['port'])
    
    response = app_client.get('/routes')
    assert response.status_code == 200

    stop_server(server)


if __name__ == '__main__':
    pytest.main()