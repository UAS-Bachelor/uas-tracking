from flask_sqlalchemy import SQLAlchemy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from exceptions import RouteNotFoundException

db = SQLAlchemy()


class DatabaseDriver:

    def __init__(self, app, db_config):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}:{}/{}'.format(db_config['user'], db_config['password'], db_config['host'], db_config['port'], db_config['database'])
        app.config['SQLALCHEMY_POOL_SIZE'] = 100
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.confirm_deleted_rows = False
        db.init_app(app)
    

    def get_live_routes(self):
        return db.session\
            .query(Route.route_id, Route.drone_id, Route.start_time, Route.end_time)\
            .filter(Route.end_time == None)\
            .distinct(Route.drone_id)\
            .order_by(Route.start_time)\
            .all()
    

    def get_data_point_by_live_route(self, route):
        return self.result_to_dict(
            db.session\
            .query(Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt)\
            .filter(Drone.id == route.drone_id, Drone.time >= route.start_time)\
            .order_by(Drone.time.desc()).first())
    

    def get_latest_live_route_by_droneid(self, droneid):
        return Route.query\
                .filter(Route.end_time == None, Route.drone_id == droneid)\
                .order_by(Route.start_time)\
                .first()
    

    def get_route_by_routeid(self, routeid):
        route = Route.query\
                    .filter(Route.route_id == routeid)\
                    .first()
        if not route:
            raise RouteNotFoundException('routeid: {}'.format(routeid))
        return route
    

    def get_route_by_droneid_and_start_time(self, droneid, start_time):
        return Route.query\
                .filter(Route.drone_id == droneid, Route.start_time == start_time)\
                .first()


    def get_data_points_by_route(self, route):
        return self.result_to_list_of_dicts(
            db.session\
            .query(Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt)\
            .filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time)\
            .all())


    def get_finished_routes(self):
        return self.result_to_list_of_dicts(
            db.session\
            .query(Route.route_id, Route.drone_id, Route.start_time, Route.end_time)\
            .filter(Route.end_time != None)\
            .order_by(Route.start_time)\
            .all())


    def delete_data_points_by_route(self, route):
        Drone.query\
            .filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time)\
            .delete()


    def delete(self, element):
        db.session.delete(element)


    def merge(self, element):
        db.session.merge(element)


    def add(self, element):
        db.session.add(element)


    def commit(self):
        db.session.commit()


    def result_to_list_of_dicts(self, results):
        list_of_dicts = []
        for result in results:
            list_of_dicts.append(
                self.result_to_dict(result)
            )
        return list_of_dicts
    

    def result_to_dict(self, result):
        return dict(zip(result.keys(), result))


class Drone(db.Model):

    __tablename__ = "drones"

    time_stamp = db.Column(db.String(255))
    time = db.Column(db.BigInteger(), primary_key=True)
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(20))
    lat = db.Column(db.Float, default=0)
    lon = db.Column(db.Float, default=0)
    alt = db.Column(db.Float, default=0)
    acc = db.Column(db.Float, default=0)
    fix = db.Column(db.SmallInteger, default=0)
    lnk = db.Column(db.SmallInteger, default=0)
    eng = db.Column(db.SmallInteger, default=0)
    sim = db.Column(db.SmallInteger)

    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])


class Route(db.Model):

    __tablename__ = "routes"

    route_id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.String(20), db.ForeignKey('drones.id'))
    start_time = db.Column(db.BigInteger())
    end_time = db.Column(db.BigInteger())

