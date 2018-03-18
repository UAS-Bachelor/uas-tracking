from drone_information import db

class Drone(db.Model):
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
