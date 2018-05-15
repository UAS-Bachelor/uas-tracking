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
        db.init_app(app)
    

    def get_route_by_routeid(self, routeid):
        route = Route.query.filter(Route.route_id == routeid).first()
        if not route:
            raise RouteNotFoundException(routeid)
        return route


    def get_data_points_by_route(self, route):
        return self.result_to_list_of_dicts(db.session.query(Drone.id, Drone.time, Drone.time_stamp, Drone.lat, Drone.lon, Drone.alt).filter(Drone.id == route.drone_id, Drone.time >= route.start_time, Drone.time <= route.end_time).all())


    def result_to_list_of_dicts(self, results):
        list_of_dicts = []
        for result in results:
            print(result)
            list_of_dicts.append(
                dict(zip(result.keys(), result))
            )
        return list_of_dicts



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

