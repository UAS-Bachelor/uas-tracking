from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Drone(db.Model):

    __tablename__ = "drones"

    time_stamp = db.Column(db.String(255))
    time = db.Column(db.BigInteger(), primary_key=True)
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(20))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    alt = db.Column(db.Float)
    acc = db.Column(db.Float)
    fix = db.Column(db.SmallInteger)
    lnk = db.Column(db.SmallInteger)
    eng = db.Column(db.SmallInteger)
    sim = db.Column(db.SmallInteger)

    def __init__(self, time_stamp, time, id, name, lat, lon, alt, acc, fix, lnk, eng, sim):
        self.time_stamp = time_stamp
        self.time = time
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.acc = acc
        self.fix = fix
        self.lnk = lnk
        self.eng = eng
        self.sim = sim


class Route_start(db.Model):

    __tablename__ = "routes_start"

    start_time = db.Column(db.BigInteger(), primary_key=True)
    id = db.Column(db.String(20), primary_key=True)

    def __init__(self, start_time, id):
        self.start_time = start_time
        self.id = id


class Route_end(db.Model):

    __tablename__ = "routes_end"

    end_time = db.Column(db.BigInteger(), primary_key=True)
    id = db.Column(db.String(20), primary_key=True)

    def __init__(self, end_time, id):
        self.end_time = end_time
        self.id = id


class Route(db.Model):

    __tablename__ = "routes"

    route_id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.String(20))
    start_time = db.Column(db.BigInteger())
    end_time = db.Column(db.BigInteger())

    def __init__(self, route_id, drone_id, start_time, end_time):
        self.route_id = route_id
        self.drone_id = drone_id
        self.start_time = start_time
        self.end_time = end_time
