import pytest
from html.parser import HTMLParser
import sys
import os
import json
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from services.api_gateway import api_gateway
from services.drone_information import drone_information
from scripts.util import config
from common import start_server, stop_server, __run_drone_information


class DataHTMLParser(HTMLParser):

    parsed_data = []

    def handle_data(self, data):
        data = data.strip()
        if data:
            self.parsed_data.append(data)


@pytest.fixture
def htmlparser():
    yield DataHTMLParser()


@pytest.fixture
def client():
    api_gateway.app.config['TESTING'] = True
    api_gateway.config = json.load(open(api_gateway.__services_config_file))
    client = api_gateway.app.test_client()
    yield client


@pytest.fixture
def drone_information():
    server = start_server(__run_drone_information, config['drone_information']['port'])
    yield server
    stop_server(server)


@pytest.fixture
def drone_data_points():
    yield [{
        'id': 919,
        'lat': 55.37000,
        'lon': 10.43000,
        'alt': 00.00000,
        'time': 1524231287
    },
    {
        'id': 919,
        'lat': 55.38050,
        'lon': 10.43000,
        'alt': 100.00000,
        'time': 1524231299
    }]


def epoch_to_datetime(epoch):
    return time.strftime('%d %b %Y, %H:%M:%S', time.gmtime(epoch))


def test_routes_service_unavailable(client):
    response = client.get('/routes')
    assert response.status_code == 503
    assert response.data.decode().strip() == 'Drone information service unavailable'


def test_routes(client, drone_data_points, htmlparser, drone_information):
    post_response = client.post('/routes', json=drone_data_points)
    routeid = post_response.data.decode().strip()
    assert post_response.status_code == 201

    get_response = client.get('/routes')
    assert get_response.status_code == 200
    htmlparser.feed(get_response.data.decode())

    droneid = str(drone_data_points[0]['id'])
    start_time = epoch_to_datetime(drone_data_points[0]['time'])
    end_time = epoch_to_datetime(drone_data_points[-1]['time'])
    assert all(item in htmlparser.parsed_data for item in (droneid, start_time, end_time))

    delete_response = client.delete('/routes/{}'.format(routeid))
    assert delete_response.status_code == 200
    assert delete_response.data.decode().strip() == routeid


def test_routes_by_routeid(client, drone_data_points, drone_information):
    post_response = client.post('/routes', json=drone_data_points)
    routeid = post_response.data.decode().strip()
    assert post_response.status_code == 201

    get_response = client.get('/routes/{}'.format(routeid))
    get_response_data = json.loads(get_response.data)
    assert get_response.status_code == 200
    
    for i in range(len(drone_data_points)):
        drone_data_points[i]['id'] = str(drone_data_points[i]['id'])
        assert all((key, value) in get_response_data[i].items() for (key, value) in drone_data_points[i].items())

    delete_response = client.delete('/routes/{}'.format(routeid))
    assert delete_response.status_code == 200
    assert delete_response.data.decode().strip() == routeid


if __name__ == '__main__':
    pytest.main()