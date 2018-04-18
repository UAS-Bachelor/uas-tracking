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

    def __init__(self, dictionary):
        print('INITTING')
        for key in dictionary:
            setattr(self, key, dictionary[key])
        if not self.time_stamp:
            print('øvski')


class Route(db.Model):

    __tablename__ = "routes"

    route_id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.String(20))
    start_time = db.Column(db.BigInteger())
    end_time = db.Column(db.BigInteger())

