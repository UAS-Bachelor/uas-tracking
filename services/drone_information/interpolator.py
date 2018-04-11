from scipy import interpolate
from time_util import epoch_to_time


def spline_interpolate(drone_route_list, interval):
    interpolated_result = []
    drone = drone_route_list[0]
    time = [drone_route['time'] for drone_route in drone_route_list]
    lat = [drone_route['lat'] for drone_route in drone_route_list]
    lon = [drone_route['lon'] for drone_route in drone_route_list]
    counter = time[0]
    end_time = time[-1]
    lat_tck = interpolate.splrep(time, lat) #cubic spline interpolation requires >3 data points
    lon_tck = interpolate.splrep(time, lon)

    while counter <= end_time:
        interpolated_lat = interpolate.splev(counter, lat_tck).tolist()
        interpolated_lon = interpolate.splev(counter, lon_tck).tolist()

        interpolated_result.append({
            'time_stamp': epoch_to_time(counter),
            'time': counter,
            'id': drone['id'],
            'lat': interpolated_lat,
            'lon': interpolated_lon
        })
        counter += interval
    return interpolated_result
