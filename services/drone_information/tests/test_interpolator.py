import pytest
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import interpolator


@pytest.fixture(scope='module')
def drone_route_list():
    yield [{
        'id': '910',
        'lat': 55.37,
        'lon': 10.43, 
        'time': 1523020346
    },
    {
        'id': '912',
        'lat': 55.38,
        'lon': 10.43,
        'time': 1523020351,
    },
    {
        'id': '912',
        'lat': 55.39,
        'lon': 10.44,
        'time': 1523020356,
    },
    {
        'id': '912',
        'lat': 55.4,
        'lon': 10.45,
        'time': 1523020361,
    }]


def test_interpolator(drone_route_list):
    interval = 2
    counter = 0
    timer = drone_route_list[0]['time']
    end_time = drone_route_list[-1]['time']
    while timer <= end_time:
        timer += interval
        counter += 1
    interpolated_result = interpolator.spline_interpolate(drone_route_list, interval)
    interpolated_result_length = len(interpolated_result)
    interpolated_result_start_time = interpolated_result[0]['time']
    interpolated_result_end_time = interpolated_result[-1]['time']
    interpolated_result_time_span = interpolated_result_end_time - interpolated_result_start_time

    assert interpolated_result_length == counter

    expected_length = (interpolated_result_time_span / interval) + 1
    assert interpolated_result_length == expected_length

    expected_interval = math.ceil(interpolated_result_time_span / interpolated_result_length)
    assert interval == expected_interval


if __name__ == '__main__':
    pytest.main()