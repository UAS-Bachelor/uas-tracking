import pytest
from unittest import mock
from flask import Flask, request
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import drone_information
from exceptions import RouteNotFoundException, MissingKeyException


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
    },
    {
        'id': 919,
        'lat': 55.39050,
        'lon': 10.43000,
        'alt': 100.00000,
        'time': 1524231304
    }, 
    {
        'id': 919,
        'lat': 55.39050,
        'lon': 10.44000,
        'alt': 100.00000,
        'time': 1524231309
    }]


@pytest.fixture
def route_data():
    yield {
        'route_id': 15, 
        'drone_id': 919, 
        'start_time': 1524231287, 
        'end_time': 1524231299
    }


@pytest.fixture
def mock_route(route_data):
    route = mock.MagicMock(**route_data)
    yield route


@pytest.fixture
def mock_drone(drone_data_points):
    drone = mock.MagicMock(**drone_data_points[0])
    yield drone


@pytest.fixture
def mock_db():
    app = Flask(__name__)
    with app.test_request_context():
        with mock.patch('drone_information.db') as mock_db:
            yield mock_db


def compare_dicts(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def raise_routenotfoundexception(routeid):
    raise RouteNotFoundException('routeid: {}'.format(routeid))


def delete_key(key, collection):
    [d.pop(key) for d in collection]


def test_get_live(mock_db, mock_route, drone_data_points):
    drone_information.db.get_live_routes.return_value = [mock_route]
    drone_information.db.get_data_point_by_live_route.return_value = drone_data_points[0]
    
    response = drone_information.get_live_drones()
    response_data = json.loads(response[0].data)
    
    assert compare_dicts(response_data[0], drone_data_points[0])


def test_get_live_no_live_drones(mock_db):
    drone_information.db.get_live_routes.return_value = []
    
    response = drone_information.get_live_drones()
    response_data = json.loads(response[0].data)
    
    assert not response_data


def test_get_live_drone_by_id(mock_db, mock_route, drone_data_points):
    drone_information.db.get_latest_live_route_by_droneid.return_value = mock_route
    drone_information.db.get_data_point_by_live_route.return_value = drone_data_points[0]

    response = drone_information.get_live_drone_by_id(919)
    response_data = json.loads(response[0].data)
    
    assert compare_dicts(response_data, drone_data_points[0])


def test_get_live_drone_by_id_not_live(mock_db):
    drone_information.db.get_latest_live_route_by_droneid.return_value = None

    response = drone_information.get_live_drone_by_id(919)
    response_data = json.loads(response[0].data)
    
    assert 'error' in response_data


def test_get_drone_routes(mock_db, route_data):
    drone_information.db.get_finished_routes.return_value = [route_data]

    response = drone_information.get_drone_routes()
    response_data = json.loads(response[0].data)
    
    assert compare_dicts(response_data[0], route_data)


def test_get_drone_routes_no_finished_routes(mock_db, route_data):
    drone_information.db.get_finished_routes.return_value = []

    response = drone_information.get_drone_routes()
    response_data = json.loads(response[0].data)
    
    assert not response_data


def test_post_drone_route_doesnt_exist(mock_db, route_data, drone_data_points):
    request._cached_data = json.dumps(drone_data_points)
    drone_information.db.get_route_by_droneid_and_start_time.return_value = None
    drone_information.db.add.side_effect = lambda route : setattr(route, 'route_id', route_data['route_id'])

    response = drone_information.post_drone_route()
    response_data = json.loads(response[0].data)

    assert response_data == route_data['route_id']


def test_post_drone_route_exists(mock_db, route_data, mock_route, drone_data_points):
    request._cached_data = json.dumps(drone_data_points)
    drone_information.db.get_route_by_droneid_and_start_time.return_value = mock_route
    drone_information.db.add.side_effect = lambda route : setattr(route, 'route_id', route_data['route_id'])

    response = drone_information.post_drone_route()
    response_data = json.loads(response[0].data)

    assert response_data == route_data['route_id']
    assert mock_route.end_time == drone_data_points[-1]['time']


def test_put_drone_route_exists(mock_db, route_data, mock_route, drone_data_points):
    request._cached_data = json.dumps(drone_data_points)
    drone_information.db.get_route_by_routeid.return_value = mock_route

    response = drone_information.put_drone_route(15)
    response_data = json.loads(response[0].data)

    assert response_data == route_data['route_id']
    assert mock_route.start_time == drone_data_points[0]['time']
    assert mock_route.end_time == drone_data_points[-1]['time']


def test_put_drone_route_doesnt_exist(mock_db, route_data, mock_route, drone_data_points):
    request._cached_data = json.dumps(drone_data_points)
    drone_information.db.get_route_by_routeid.return_value = None

    #with pytest.raises(RouteNotFoundException):
    drone_information.put_drone_route(15)
    drone_information.db.rollback.assert_called()


def test_post_illegal_route_missing_time(drone_data_points):
    delete_key('time', drone_data_points)
    with pytest.raises(MissingKeyException) as exception_info:
        drone_information.__fit_drone_data_point(drone_data_points[0])
        assert 'error' in exception_info.value
        assert 'missing key: time' == exception_info.value['error']


def test_post_illegal_route_missing_lat(drone_data_points):
    delete_key('lat', drone_data_points)
    with pytest.raises(MissingKeyException) as exception_info:
        drone_information.__fit_drone_data_point(drone_data_points[0])
        assert 'error' in exception_info.value
        assert 'missing key: lat' == exception_info.value['error']


def test_post_illegal_route_missing_lon(drone_data_points):
    delete_key('lon', drone_data_points)
    with pytest.raises(MissingKeyException) as exception_info:
        drone_information.__fit_drone_data_point(drone_data_points[0])
        assert 'error' in exception_info.value
        assert 'missing key: lon' == exception_info.value['error']


def test_post_illegal_route_missing_alt(drone_data_points):
    delete_key('alt', drone_data_points)
    with pytest.raises(MissingKeyException) as exception_info:
        drone_information.__fit_drone_data_point(drone_data_points[0])
        assert 'error' in exception_info.value
        assert 'missing key: alt' == exception_info.value['error']


def test_post_illegal_route_defaulted_id(drone_data_points):
    delete_key('id', drone_data_points)
    assert 'id' not in drone_data_points[0]
    corrected_point = drone_information.__fit_drone_data_point(drone_data_points[0])
    assert 'id' in corrected_point
    assert corrected_point['id'] == 910


def test_get_route_points_by_routeid(mock_db, mock_route, drone_data_points):
    drone_information.db.get_route_by_routeid.return_value = mock_route
    drone_information.db.get_data_points_by_route.return_value = drone_data_points

    response = drone_information.get_route_points_by_routeid(15)
    response_data = json.loads(response[0].data)

    assert compare_dicts(response_data, drone_data_points)


def test_get_route_points_by_routeid_no_route(mock_db):
    drone_information.db.get_route_by_routeid.side_effect = raise_routenotfoundexception

    response = drone_information.get_route_points_by_routeid(15)
    response_data = json.loads(response[0].data)

    assert 'error' in response_data


def test_delete_route_by_routeid(mock_db, mock_route):
    drone_information.db.get_route_by_routeid.return_value = mock_route

    response = drone_information.delete_route_by_routeid(15)
    response_data = json.loads(response[0].data)

    assert response_data == mock_route.route_id


def test_delete_route_by_routeid_no_route(mock_db):
    drone_information.db.get_route_by_routeid.side_effect = raise_routenotfoundexception

    response = drone_information.delete_route_by_routeid(15)
    response_data = json.loads(response[0].data)

    assert 'error' in response_data


def test_delete_route_and_data_points(mock_db, mock_route):
    drone_information.delete_route_and_data_points(mock_route)

    drone_information.db.delete_data_points_by_route.assert_called()
    drone_information.db.delete.assert_called()


if __name__ == '__main__':
    pytest.main()