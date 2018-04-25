from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

