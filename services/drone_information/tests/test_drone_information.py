import pytest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from drone_information import app


@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


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


@pytest.fixture
def post_legal_route_response(client, drone_data_points):
    response = client.post('/routes', json=drone_data_points)
    yield response
    delete_route(client, int(response.data))


def test_illegal_url(client):
    response = client.get('/illegalurl/does/not/exist')
    assert response.status_code == 404


def test_illegal_method(client):
    response = client.delete('/')
    assert response.status_code == 405


def test_post_legal_route(post_legal_route_response):
    assert post_legal_route_response.status_code == 201


def test_post_illegal_route(client, drone_data_points):
    [drone_data_point.pop('lat') for drone_data_point in drone_data_points]
    response = client.post('/routes', json=drone_data_points)
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)


def test_delete_route(client, post_legal_route_response):
    delete_response = delete_route(client, int(post_legal_route_response.data))
    assert delete_response.status_code == 200
    assert int(post_legal_route_response.data) == int(delete_response.data)


def test_delete_illegal_route(client):
    response = delete_route(client, -1)
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)


def test_get_routes(client, post_legal_route_response):
    get_response = get_routes(client)
    assert any(route['route_id'] == int(post_legal_route_response.data) for route in json.loads(get_response.data))


def test_get_route_by_routeid(client, drone_data_points, post_legal_route_response):
    get_response = client.get('/routes/{}'.format(int(post_legal_route_response.data)))
    assert get_response.status_code == 200
    received_drone_data_points = json.loads(get_response.data)

    for drone_data_point in drone_data_points:
        for key, value in drone_data_point.items():
            for received_drone_data_point in received_drone_data_points:
                assert key, value in received_drone_data_point.items()


def test_route_get_by_routeid_illegal(client):
    response = client.get('/routes/-1')
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)


def get_routes(client):
    response = client.get('/routes')
    return response


def delete_route(client, routeid):
    response = client.delete('/routes/{}'.format(routeid))
    return response


if __name__ == '__main__':
    pytest.main()