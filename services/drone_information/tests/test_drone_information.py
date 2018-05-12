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


@pytest.fixture(scope='module')
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


def test_illegal_url(client):
    response = client.get('/illegalurl')
    assert response.status_code == 404


def test_illegal_method(client):
    response = client.delete('/')
    assert response.status_code == 405


def test_routes_post_legal_and_get(client, drone_data_points):
    post_response = post_legal_route(client, drone_data_points)
    assert post_response.status_code == 200
    get_response = get_routes(client)
    assert any(route['route_id'] == int(post_response.data) for route in json.loads(get_response.data))
    delete_route(client, int(post_response.data))


def test_routes_post_legal_and_delete(client, drone_data_points):
    post_response = post_legal_route(client, drone_data_points)
    assert post_response.status_code == 200
    delete_response = delete_route(client, int(post_response.data))
    print(post_response.data)
    print(delete_response.data)
    assert int(post_response.data) == int(delete_response.data)


def test_routes_post_illegal(client):
    response = post_illegal_route(client)
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)


def test_routes_delete_illegal(client):
    response = delete_route(client, -1)
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)


def test_route_get_by_routeid(client, drone_data_points):
    post_response = post_legal_route(client, drone_data_points)
    assert post_response.status_code == 200
    get_response = client.get('/routes/{}'.format(int(post_response.data)))
    assert get_response.status_code == 200
    received_drone_data_points = json.loads(get_response.data)

    for drone_data_point in drone_data_points:
        for key, value in drone_data_point.items():
            for received_drone_data_point in received_drone_data_points:
                assert key, value in received_drone_data_point.items()
    delete_route(client, int(post_response.data))


def test_route_get_by_routeid_fail(client, drone_data_points):
    response = client.get('/routes/-1')
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)


def get_routes(client):
    response = client.get('/routes')
    return response


def post_legal_route(client, drone_data_points):
    response = client.post('/routes', json=drone_data_points)
    return response


def post_illegal_route(client):
    response = client.post('/routes', json=[{
        'id': 919,
        'lon': 10.43000,
        'alt': 00.00000,
        'time': 1524231287
    },
    {
        'id': 919,
        'lon': 10.43000,
        'alt': 100.00000,
        'time': 1524231299
    }])
    return response


def delete_route(client, routeid):
    response = client.delete('/routes/{}'.format(routeid))
    return response


if __name__ == '__main__':
    pytest.main()