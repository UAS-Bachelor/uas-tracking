import pytest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from drone_information import app


@pytest.fixture
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


def test_post_illegal_route_missing_time(client, drone_data_points):
    delete_key('time', drone_data_points)
    response = client.post('/routes', json=drone_data_points)
    response_text = json.loads(response.data)
    assert response.status_code == 400
    assert 'error' in response_text
    assert 'missing key: time' == response_text['error']


def test_post_route_default_id(client, drone_data_points):
    delete_key('id', drone_data_points)
    post_response = post_route(client, drone_data_points)
    get_response = client.get('/routes/{}'.format(int(post_response.data)))
    assert get_response.status_code == 200
    assert json.loads(get_response.data)[0]['id'] == '910'
    
    delete_route(client, int(post_response.data))


def test_put_existing_route_to_extend_it(client, drone_data_points):
    first_post_response = post_route(client, [dict(drone_data_points[0])])
    first_get_response = client.get('/routes/{}'.format(int(first_post_response.data)))
    first_response_text = json.loads(first_get_response.data)
    assert first_get_response.status_code == 200
    assert len(first_response_text) == 1
    assert first_response_text[-1]['time'] == drone_data_points[0]['time']

    second_put_response = put_route(client, drone_data_points, int(first_post_response.data))
    second_get_response = client.get('/routes/{}'.format(int(first_post_response.data)))
    second_response_text = json.loads(second_get_response.data)
    assert second_get_response.status_code == 200
    assert len(second_response_text) == 2
    assert second_response_text[-1]['time'] == drone_data_points[1]['time']

    assert first_post_response.data == second_put_response.data
    
    delete_route(client, int(second_put_response.data))


def test_put_route_that_does_not_exist(client, drone_data_points):
    put_response = put_route(client, drone_data_points, '-1')
    
    assert put_response.status_code == 404


def test_delete_route(client, post_legal_route_response):
    delete_response = delete_route(client, int(post_legal_route_response.data))
    assert delete_response.status_code == 200
    assert int(post_legal_route_response.data) == int(delete_response.data)


def test_delete_illegal_route(client):
    response = delete_route(client, -1)
    assert response.status_code == 404
    assert 'error' in json.loads(response.data)


def test_get_routes(client, post_legal_route_response):
    get_response = client.get('/routes')
    retrieved_routes = json.loads(get_response.data)
    routeid = int(post_legal_route_response.data)

    assert get_response.status_code == 200
    assert any(route['route_id'] == routeid for route in retrieved_routes)


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


def test_get_live(client):
    response = client.get('/live')
    assert response.status_code == 200
    assert type(json.loads(response.data) == list)


'''def test_get_live_by_id(client):
    response = client.get('/live/1')
    assert response.status_code == 200
    assert type(json.loads(response.data) == list)
'''

def test_get_live_by_id_illegal(client):
    droneid = -1
    response = client.get('/live/{}'.format(droneid))
    response_text = json.loads(response.data)
    assert response.status_code == 404
    assert 'error' in response_text
    assert 'drone with droneid {} is currently not in flight'.format(droneid) == response_text['error']


def get_routes(client):
    response = client.get('/routes')
    return response


def post_route(client, drone_data_points):
    response = client.post('/routes', json=drone_data_points)
    return response


def put_route(client, drone_data_points, routeid):
    response = client.put('/routes/{}'.format(routeid), json=drone_data_points)
    return response


def delete_route(client, routeid):
    response = client.delete('/routes/{}'.format(routeid))
    return response

def delete_key(key, collection):
    [d.pop(key) for d in collection]


if __name__ == '__main__':
    pytest.main()