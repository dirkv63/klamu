# import logging
import time
from klamu import db, lm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Cd(db.Model):
    """
    Table with CD Information
    """
    __tablename__ = "cd"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.Integer, nullable=False)
    modified = db.Column(db.Integer, nullable=False)
    identificatie = db.Column(db.Text)
    titel = db.Column(db.Text, nullable=False)
    uitgever_id = db.Column(db.Integer, db.ForeignKey('uitgever.id'))
    uitgever = db.relationship("Uitgever", backref='cd')

class Dirigent(db.Model):
    """
    Table with Dirigent Information
    """
    __tablename = "dirigent"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)
    voornaam = db.Column(db.Text)

class Komponist(db.Model):
    """"
    Table with Komponist Information
    """
    __tablename__ = 'komponist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.Integer, nullable=False)
    modified = db.Column(db.Integer, nullable=False)
    naam = db.Column(db.Text, nullable=False)
    voornaam = db.Column(db.Text)

class Kompositie(db.Model):
    """
    Table with Kompositie Information.
    """
    __tablename__ = 'kompositie'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)
    komponist_id = db.Column(db.Integer, db.ForeignKey('komponist.id'))
    komponist = db.relationship('Komponist', backref='kompositie')

class Uitgever(db.Model):
    """
    Table with Uitgever Information
    """
    __tablename = "uitgever"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)

class Uitvoerders(db.Model):
    """
    Table with Uitvoerders Information
    """
    __tablename = "uitvoerders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)

class Uitvoering(db.Model):
    """
    Table with Uitgever Information
    """
    __tablename = "uitgever"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.Integer, nullable=False)
    modified = db.Column(db.Integer, nullable=False)
    volgnummer = db.Column(db.Integer)
    cd_id = db.Column(db.Integer, db.ForeignKey('cd.id'))
    cd = db.relationship('Cd', backref='uitvoering')
    uitvoerders_id = db.Column(db.Integer, db.ForeignKey('uitvoerders.id'))
    uitvoerders = db.relationship('Uitvoerders', backref='uitvoering')
    dirigent_id = db.Column(db.Integer, db.ForeignKey('dirigent.id'))
    dirigent = db.relationship('Dirigent', backref='uitvoering')
    kompositie_id = db.Column(db.Integer, db.ForeignKey('kompositie.id'), nullable=False)
    kompositie = db.relationship('Kompositie', backref='uitvoering')

class History(db.Model):
    """
    Table remembering which node is selected when.
    """
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)

    @staticmethod
    def add(nid):
        params = dict(
            timestamp=int(time.time()),
            node_id=nid
        )
        hist_inst = History(**params)
        db.session.add(hist_inst)
        db.session.commit()
        return



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(username, password):
        user = User()
        user.username = username
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update_password(user, password):
        user.password_hash = generate_password_hash(password)
        db.session.commit(user)
        return

    def __repr__(self):
        return "<User: {user}>".format(user=self.username)


def init_session(dbconn, echo=False):
    """
    This function configures the connection to the database and returns the session object.

    :param dbconn: Name of the sqlite3 database.
    :param echo: True / False, depending if echo is required. Default: False
    :return: session object.
    """
    conn_string = "sqlite:///{db}".format(db=dbconn)
    engine = set_engine(conn_string, echo)
    session = set_session4engine(engine)
    return session


def set_engine(conn_string, echo=False):
    engine = create_engine(conn_string, echo=echo)
    return engine


def set_session4engine(engine):
    session_class = sessionmaker(bind=engine)
    session = session_class()
    return session


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_cd(nid):
    """
    Function to return information on a single CD.

    :param nid: ID of the CD.
    """
    cd = Cd.query.filter_by(id=nid).one()
    return cd

def get_cds():
    """
    Function to return list of all CDs.
    """
    cds = Cd.query
    return cds

def get_komponist(nid):
    komponist = Komponist.query.filter_by(id=nid).one()
    return komponist

def get_komponisten():
    """
    Function to return list of all Komponisten.
    """
    komponisten = Komponist.query
    return komponisten

def get_komposities():
    """
    Function to return list of all komposities.
    """
    komposities = Kompositie.query
    return komposities

def get_cd_uitvoeringen(cd):
    """
    Function to return the content of a CD.

    :param cd: Id of the CD
    """
    uitvoeringen = Uitvoering.query.filter_by(cd_id=cd)
    return uitvoeringen
