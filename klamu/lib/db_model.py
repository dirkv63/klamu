# import logging
import time
from klamu import db, lm
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

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

    """
    def __init__(self):
        self.nid = Cd.id
    """

    @hybrid_property
    def items(self):
        """
        Returns the number of uitvoeringen on a CD.
        """
        uit_list = [uit.id for uit in self.uitvoering]
        return len(uit_list)

    @staticmethod
    def delete(nid):
        """
        This method will delete the CD on condition that there is no link to uitvoeringen.

        :param nid: Id of the cd.
        :return: Dictionary with nid (ID of the cd), msg and status for flash.
        """
        try:
            query = db.session.query(Cd, db.func.count(Uitvoering.id).label("Cnt")) \
                .outerjoin(Uitvoering)\
                .filter(Cd.id == nid)\
                .group_by(Uitvoering.cd_id).one()
        except NoResultFound:
            msg = f"CD (id: {nid}) is niet gevonden!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        cnt = query.Cnt
        cd = query.Cd
        if cnt == 0:
            msg = f"CD {cd.titel} is verwijderd."
            current_app.logger.info(msg)
            db.session.delete(cd)
            db.session.commit()
            return dict(nid=-1, msg=msg, status="success")
        else:
            msg = f"CD {cd.titel} is nog verbonden met {cnt} uitvoering(en)."
            current_app.logger.info(msg)
            return dict(nid=nid, msg=msg, status="error")

    @staticmethod
    def update(**params):
        """
        This method will add or edit the CD.

        :param params: Dictionary with titel, identificatie en uitgever. ID is optional, If ID then update else add CD.
        :return: ID of the CD.
        """
        now = int(time.time())
        params['modified'] = now
        if params["uitgever_id"] == '-1':
            params["uitgever_id"] = None
        if len(params['identificatie']) == 0:
            params['identificatie'] = None
        if 'id' in params:
            # Update record
            cd = db.session.query(Cd).filter_by(id=params['id']).one()
            cd.titel = params["titel"]
            cd.identificatie = params["identificatie"]
            cd.uitgever_id = params["uitgever_id"]
        else:
            # Insert new record
            params['created'] = now
            cd = Cd(**params)
            db.session.add(cd)
        db.session.commit()
        db.session.refresh(cd)
        return cd.id


class Dirigent(db.Model):
    """
    Table with Dirigent Information
    """
    __tablename__ = "dirigent"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)
    voornaam = db.Column(db.Text)
    fnaam = db.column_property(naam + " " + voornaam)

    @hybrid_property
    def items(self):
        """
        Returns the number of uitvoeringen.
        """
        uit_list = [uit.id for uit in self.uitvoering]
        return len(uit_list)

    @staticmethod
    def delete(nid):
        """
        This method will delete the Dirigent on condition that there is no link to uitvoeringen.

        :param nid: Id of the dirigent.
        :return: Dictionary with nid (ID of the dirigent), msg and status for flash.
        """
        try:
            query = db.session.query(Dirigent, db.func.count(Uitvoering.id).label("Cnt")) \
                .outerjoin(Uitvoering)\
                .filter(Dirigent.id == nid)\
                .group_by(Uitvoering.dirigent_id).one()
        except NoResultFound:
            msg = f"Dirigent (id: {nid}) is niet gevonden!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        cnt = query.Cnt
        dirigent = query.Dirigent
        if cnt == 0:
            msg = f"Dirigent {dirigent.voornaam} {dirigent.naam} is verwijderd."
            current_app.logger.info(msg)
            db.session.delete(dirigent)
            db.session.commit()
            return dict(nid=-1, msg=msg, status="success")
        else:
            msg = f"Dirigent {dirigent.voornaam} {dirigent.naam} is nog verbonden met {cnt} uitvoering(en)."
            current_app.logger.info(msg)
            return dict(nid=nid, msg=msg, status="error")

    @staticmethod
    def update(**params):
        """
        This method will add or edit the Dirigent. It will add only if Dirigent naam+voornaam did not exist before.

        :param params: Dictionary with naam, voornaam and optional ID, If ID then update else add Dirigent.
        :return: Dictionary with nid (ID of the dirigent), msg and status for flash.
        """
        naam = params['naam']
        voornaam = params['voornaam']
        try:
            check_dirigent = Dirigent.query.filter(db.func.lower(Dirigent.naam)==naam.lower(),
                                                   db.func.lower(Dirigent.voornaam)==voornaam.lower()).one()
        except NoResultFound:
            check_id = None
        except MultipleResultsFound:
            msg = f"Dirigent {voornaam} {naam} is niet uniek!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        else:
            check_id = check_dirigent.id
        if 'id' in params:
            nid = int(params['id'])
            # Update record
            dirigent = Dirigent.query.filter_by(id=nid).one()
            if check_id:
                if nid == int(check_id):
                    msg = f"Dirigent {voornaam} {naam} is niet veranderd."
                else:
                    msg = f"Dirigent {voornaam} {naam} niet aangepast, bestaat al."
                    return dict(nid=check_id, msg=msg, status="error")
            else:
                msg = f"Dirigent {voornaam} {naam} is aangepast."
            dirigent.naam = naam
            dirigent.voornaam = voornaam
        else:
            if check_id:
                msg = f"Dirigent {voornaam} {naam} niet aangepast, bestaat al."
                return dict(nid=check_id, msg=msg, status="error")
            else:
                # Insert new record
                msg = f"Dirigent {voornaam} {naam} is toegevoegd."
                dirigent = Dirigent(**params)
                db.session.add(dirigent)
        db.session.commit()
        db.session.refresh(dirigent)
        return dict(nid=dirigent.id, msg=msg, status="success")

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
    fnaam = db.column_property(naam + " " + voornaam)

    @hybrid_property
    def komposities(self):
        """
        Returns the number of komposities per komponist.
        """
        komp_list = [komp.id for komp in self.kompositie]
        return len(komp_list)

    @hybrid_property
    def items(self):
        """
        Returns the number of uitvoeringen per komponist.
        """
        cnt = 0
        for kompositie in self.kompositie:
            for _ in kompositie.uitvoering:
                cnt += 1
        return cnt

    @staticmethod
    def delete(nid):
        """
        This method will delete the Komponist on condition that there is no link to komposities.

        :param nid: Id of the komponist.
        :return: Dictionary with nid (ID of the komponist), msg and status for flash.
        """
        try:
            query = db.session.query(Komponist, db.func.count(Kompositie.id).label("Cnt")) \
                .outerjoin(Kompositie)\
                .filter(Komponist.id == nid)\
                .group_by(Kompositie.komponist_id).one()
        except NoResultFound:
            msg = f"Komponist (id: {nid}) is niet gevonden!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        cnt = query.Cnt
        komponist = query.Komponist
        if cnt == 0:
            msg = f"Komponist {komponist.voornaam} {komponist.naam} verwijderd."
            current_app.logger.info(msg)
            db.session.delete(komponist)
            db.session.commit()
            return dict(nid=-1, msg=msg, status="success")
        else:
            msg = f"Komponist {komponist.voornaam} {komponist.naam} nog verbonden met {cnt} uitvoering(en)."
            current_app.logger.info(msg)
            return dict(nid=nid, msg=msg, status="error")

    @staticmethod
    def update(**params):
        """
        This method will add or edit the Komponist. It will add only if Komponist naam+voornaam did not exist before.

        :param params: Dictionary with naam, voornaam and optional ID, If ID then update else add Komponist.
        :return: Dictionary with nid (ID of the komponist), msg and status for flash.
        """
        now = int(time.time())
        naam = params['naam']
        voornaam = params['voornaam']
        try:
            check_komponist = Komponist.query.filter(db.func.lower(Komponist.naam)==naam.lower(),
                                                     db.func.lower(Komponist.voornaam)==voornaam.lower()).one()
        except NoResultFound:
            check_id = None
        except MultipleResultsFound:
            msg = f"Komponist {voornaam} {naam} is niet uniek!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        else:
            check_id = check_komponist.id
        if 'id' in params:
            nid = int(params['id'])
            # Update record
            komponist = Komponist.query.filter_by(id=nid).one()
            if check_id:
                if nid == int(check_id):
                    msg = f"Komponist {voornaam} {naam} is niet veranderd."
                else:
                    msg = f"Komponist {voornaam} {naam} niet aangepast, bestaat al."
                    return dict(nid=check_id, msg=msg, status="error")
            else:
                msg = f"Komponist {voornaam} {naam} is aangepast."
            komponist.naam = naam
            komponist.voornaam = voornaam
            komponist.modified = now
        else:
            if check_id:
                msg = f"Komponist {voornaam} {naam} niet aangepast, bestaat al."
                return dict(nid=check_id, msg=msg, status="error")
            else:
                # Insert new record
                msg = f"Komponist {voornaam} {naam} is toegevoegd."
                params['created'] = now
                params['modified'] = now
                komponist = Komponist(**params)
                db.session.add(komponist)
        db.session.commit()
        db.session.refresh(komponist)
        return dict(nid=komponist.id, msg=msg, status="success")

class Kompositie(db.Model):
    """
    Table with Kompositie Information.
    """
    __tablename__ = 'kompositie'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)
    komponist_id = db.Column(db.Integer, db.ForeignKey('komponist.id'))
    komponist = db.relationship('Komponist', backref='kompositie')

    @hybrid_property
    def items(self):
        """
        Returns the number of uitvoeringen on a CD.
        """
        uit_list = [uit.id for uit in self.uitvoering]
        return len(uit_list)

    @staticmethod
    def delete(nid):
        """
        This method will delete the Kompositie on condition that there is no link to uitvoering.

        :param nid: Id of the kompositie.
        :return: Dictionary with nid (ID of the kompositie), msg and status for flash.
        """
        try:
            query = db.session.query(Kompositie, db.func.count(Uitvoering.id).label("Cnt")) \
                .outerjoin(Uitvoering)\
                .filter(Kompositie.id == nid)\
                .group_by(Uitvoering.kompositie_id).one()
        except NoResultFound:
            msg = f"Kompositie (id: {nid}) is niet gevonden!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        cnt = query.Cnt
        kompositie = query.Kompositie
        if cnt == 0:
            msg = f"Kompositie {kompositie.naam} verwijderd."
            current_app.logger.info(msg)
            db.session.delete(kompositie)
            db.session.commit()
            return dict(nid=-1, msg=msg, status="success")
        else:
            msg = f"Kompositie {kompositie.naam} nog verbonden met {cnt} uitvoering(en)."
            current_app.logger.info(msg)
            return dict(nid=nid, msg=msg, status="error")

    @staticmethod
    def update(**params):
        """
        This method will add or edit the Kompositie.

        :param params: Dictionary with uitvoering and kompositie attributes.
        :return: Dictionary with nid (ID of the uitvoering), msg and status for flash.
        """
        if params['komponist_id'] == -1:
            # Komponist Not set, use 'Anoniem'.
            params['komponist_id'] = 500
        if 'id' in params:
            nid = int(params['id'])
            # Update record
            kompositie = Kompositie.query.filter_by(id=nid).one()
            kompositie.naam = params['naam']
            kompositie.komponist_id = params['komponist_id']
            msg = "Kompositie is aangepast."
        else:
            # Insert new record
            msg = "Kompositie is toegevoegd."
            kompositie = Kompositie(**params)
            db.session.add(kompositie)
        db.session.commit()
        db.session.refresh(kompositie)
        return dict(nid=kompositie.id, msg=msg, status="success")

class Uitgever(db.Model):
    """
    Table with Uitgever Information
    """
    __tablename__ = "uitgever"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)

    @hybrid_property
    def items(self):
        """
        Returns the number of CDs for an Uitgever.
        """
        uit_list = [uit.id for uit in self.cd]
        return len(uit_list)

    @staticmethod
    def delete(nid):
        """
        This method will delete the Uitgever on condition that there is no link to CDs.

        :param nid: Id of the uitgever.
        :return: Dictionary with nid (ID of the uitgever), msg and status for flash.
        """
        try:
            query = db.session.query(Uitgever, db.func.count(Cd.id).label("Cnt")) \
                .outerjoin(Cd)\
                .filter(Uitgever.id == nid)\
                .group_by(Cd.uitgever_id).one()
        except NoResultFound:
            msg = f"Uitgever (id: {nid}) is niet gevonden!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        cnt = query.Cnt
        uitgever = query.Uitgever
        if cnt == 0:
            msg = f"Uitgever {uitgever.naam} verwijderd."
            current_app.logger.info(msg)
            db.session.delete(uitgever)
            db.session.commit()
            return dict(nid=-1, msg=msg, status="success")
        else:
            msg = f"Uitgever {uitgever.naam} nog verbonden met {cnt} cd(s)."
            current_app.logger.info(msg)
            return dict(nid=nid, msg=msg, status="error")

    @staticmethod
    def update(**params):
        """
        This method will add or edit the Uitgever. It will add only if Uitgever naam did not exist before.

        :param params: Dictionary with naam and optional ID, If ID then update else add Uitgever.
        :return: Dictionary with nid (ID of the uitgever), msg and status for flash.
        """
        try:
            check_uitgever = Uitgever.query.filter(db.func.lower(Uitgever.naam)==params['naam'].lower()).one()
        except NoResultFound:
            check_id = None
        except MultipleResultsFound:
            msg = f"Uitgever {params['naam']} is niet uniek!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        else:
            check_id = check_uitgever.id
        if 'id' in params:
            nid = int(params['id'])
            # Update record
            uitgever = Uitgever.query.filter_by(id=params['id']).one()
            if check_id:
                if nid == int(check_id):
                    msg = f"Uitgever {params['naam']} is niet veranderd."
                else:
                    msg = f"Uitgever {params['naam']} niet aangepast, bestaat al."
                    return dict(nid=check_id, msg=msg, status="error")
            else:
                msg = f"Uitgever {params['naam']} is aangepast."
            uitgever.naam = params["naam"]
        else:
            if check_id:
                msg = f"Uitgever {params['naam']} niet aangepast, bestaat al."
                return dict(nid=check_id, msg=msg, status="error")
            else:
                # Insert new record
                msg = f"Uitgever {params['naam']} is toegevoegd."
                uitgever = Uitgever(**params)
                db.session.add(uitgever)
        db.session.commit()
        db.session.refresh(uitgever)
        return dict(nid=uitgever.id, msg=msg, status="success")

class Uitvoerders(db.Model):
    """
    Table with Uitvoerders Information
    """
    __tablename__ = "uitvoerders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.Text, nullable=False)

    @hybrid_property
    def items(self):
        """
        Returns the number of uitvoeringen on a CD.
        """
        uit_list = [uit.id for uit in self.uitvoering]
        return len(uit_list)

    @staticmethod
    def delete(nid):
        """
        This method will delete the Uitvoerders on condition that there is no link to uitvoeringen.

        :param nid: Id of the uitvoerders.
        :return: Dictionary with nid (ID of the uitvoerders), msg and status for flash.
        """
        try:
            query = db.session.query(Uitvoerders, db.func.count(Uitvoering.id).label("Cnt")) \
                .outerjoin(Uitvoering)\
                .filter(Uitvoerders.id == nid)\
                .group_by(Uitvoering.uitvoerders_id).one()
        except NoResultFound:
            msg = f"Uitvoerders (id: {nid}) is niet gevonden!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        cnt = query.Cnt
        uitvoerders = query.Uitvoerders
        if cnt == 0:
            msg = f"Uitvoerders {uitvoerders.naam} verwijderd."
            current_app.logger.info(msg)
            db.session.delete(uitvoerders)
            db.session.commit()
            return dict(nid=-1, msg=msg, status="success")
        else:
            msg = f"Uitvoerders {uitvoerders.naam} nog verbonden met {cnt} uitvoering(en)."
            current_app.logger.info(msg)
            return dict(nid=nid, msg=msg, status="error")

    @staticmethod
    def update(**params):
        """
        This method will add or edit the Uitvoerders. It will add only if Uitvoerders naam did not exist before.

        :param params: Dictionary with naam and optional ID, If ID then update else add Uitvoerders.
        :return: Dictionary with nid (ID of the uitvoerders), msg and status for flash.
        """
        naam = params['naam']
        try:
            check_uitvoerders = Uitvoerders.query.filter(db.func.lower(Uitvoerders.naam)==naam.lower()).one()
        except NoResultFound:
            check_id = None
        except MultipleResultsFound:
            msg = f"Uitvoerders {naam} is niet uniek!"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        else:
            check_id = check_uitvoerders.id
        if 'id' in params:
            nid = int(params['id'])
            # Update record
            uitvoerders = Uitvoerders.query.filter_by(id=nid).one()
            if check_id:
                if nid == int(check_id):
                    msg = f"Uitvoerders {naam} is niet veranderd."
                else:
                    msg = f"Uitvoerders {naam} niet aangepast, bestaat al."
                    return dict(nid=check_id, msg=msg, status="error")
            else:
                msg = f"Uitvoerders {naam} is aangepast."
            uitvoerders.naam = naam
        else:
            if check_id:
                msg = f"Uitvoerders {naam} niet aangepast, bestaat al."
                return dict(nid=check_id, msg=msg, status="error")
            else:
                # Insert new record
                msg = f"Uitvoerders {naam} is toegevoegd."
                uitvoerders = Uitvoerders(**params)
                db.session.add(uitvoerders)
        db.session.commit()
        db.session.refresh(uitvoerders)
        return dict(nid=uitvoerders.id, msg=msg, status="success")

class Uitvoering(db.Model):
    """
    Table with Uitvoering Information
    """
    __tablename__ = "uitvoering"
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

    @staticmethod
    def delete(nid):
        """
        This method will delete the Uitvoering.

        :param nid: Id of the uitvoering.
        :return: Dictionary with nid (ID of the uitvoering), msg and status for flash.
        """
        try:
            uitvoering = Uitvoering.query.filter_by(id=nid).one()
        except NoResultFound:
            msg = f"Uitvoering met ID {nid} is niet gevonden"
            current_app.logger.error(msg)
            return dict(nid=-1, msg=msg, status="error")
        else:
            msg = f"Uitvoering met ID {nid} verwijderd."
            current_app.logger.info(msg)
            db.session.delete(uitvoering)
            db.session.commit()
            return dict(nid=-1, msg=msg, status="success")

    @staticmethod
    def update(**params):
        """
        This method will add or edit the Uitvoering.

        :param params: Dictionary with uitvoering and kompositie attributes.
        :return: Dictionary with nid (ID of the uitvoering), msg and status for flash.
        """
        now = int(time.time())
        params['modified'] = now
        if params['uitvoerders_id'] == -1:
            params['uitvoerders_id'] = None
        if params['dirigent_id'] == -1:
            params['dirigent_id'] = None
        if 'id' in params:
            nid = int(params['id'])
            # Update record
            uitvoering = Uitvoering.query.filter_by(id=nid).one()
            uitvoering.volgnummer = params['volgnummer']
            uitvoering.cd_id = params['cd_id']
            uitvoering.uitvoerders_id = params['uitvoerders_id']
            uitvoering.dirigent_id = params['dirigent_id']
            uitvoering.kompositie_id = params['kompositie_id']
            msg = "Uitvoering is aangepast."
        else:
            # Insert new record
            msg = "Uitvoering is toegevoegd."
            params['created'] = now
            uitvoering = Uitvoering(**params)
            db.session.add(uitvoering)
        db.session.commit()
        db.session.refresh(uitvoering)
        return dict(nid=uitvoering.id, msg=msg, status="success")

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

def get_cds(nid=None):
    """
    Function to return list of all CDs.

    :param nid: Id of the uitgever or None for all CDs.
    """
    if nid:
        cds = Cd.query.filter_by(uitgever_id=nid)
    else:
        cds = Cd.query
    return cds

def get_dirigent(nid):
    dirigent = Dirigent.query.filter_by(id=nid).one()
    return dirigent

def get_dirigent_pairs():
    """
    Function to return list of dirigenten in pairs dirigent.id, dirigent.voornaam + naam.
    This can be used in a SelectField.
    """
    dirigenten = Dirigent.query.order_by(Dirigent.naam.asc())
    res = [(dirigent.id, f"{dirigent.fnaam}") for dirigent in dirigenten]
    return res

def get_dirigenten():
    """
    Function to return list of all Dirigenten and number of Uitvoeringen.
    """
    return Dirigent.query

def get_dirigent_uitvoeringen(dirigent_id):
    """
    Function to get uitvoeringen for dirigent.

    :param dirigent_id: Id of the dirigent
    """
    uitvoeringen = Uitvoering.query.filter_by(dirigent_id=dirigent_id)
    return uitvoeringen

def get_komponist(nid):
    komponist = Komponist.query.filter_by(id=nid).one()
    return komponist

def get_komponist_pairs():
    """
    Function to return list of komponisten in pairs komponist.id, komponist.voornaam + naam.
    This can be used in a SelectField.
    """
    komponisten = Komponist.query.order_by(Komponist.naam.asc())
    res = [(komponist.id, f"{komponist.fnaam}") for komponist in komponisten]
    return res

def get_komponist_uitvoeringen(komponist_id):
    """
    Function to get uitvoeringen for a komponist.

    :param komponist_id: Id of the komponist
    """
    uitvoeringen = db.session.query(Uitvoering).join(Kompositie).filter(Kompositie.komponist_id==komponist_id)
    return uitvoeringen

def get_komponisten():
    """
    Function to return list of all Komponisten and number of Komposities.
    """
    return Komponist.query

def get_kompositie(nid):
    kompositie = Kompositie.query.filter_by(id=nid).one()
    return kompositie

def get_komposities_for_komponist(nid):
    komposities = Kompositie.query.filter_by(komponist_id=nid).order_by(Kompositie.naam.asc())
    return komposities

def get_kompositie_pairs(komponist_id):
    """
    Function to return list of kompositie in pairs kompositie.id, kompositie.naam.
    This can be used in a SelectField.

    :param komponist_id: ID of the komponist for which pairs are required. Komponist_id > 0 for valid komponist.
    """
    if int(komponist_id) > 0:
        komposities = Kompositie.query.filter_by(komponist_id=komponist_id).order_by(Kompositie.naam.asc())
    else:
        komposities = Kompositie.query.order_by(Kompositie.naam.asc())
    res = [(kompositie.id, kompositie.naam) for kompositie in komposities]
    return res

def get_kompositie_uitvoeringen(kompositie_id):
    """
    Function to get uitvoeringen for kompositie.

    :param kompositie_id: Id of the kompositie
    """
    uitvoeringen = Uitvoering.query.filter_by(kompositie_id=kompositie_id)
    return uitvoeringen

def get_komposities():
    """
    Function to return list of all komposities.
    """
    return Kompositie.query

def get_cd_uitvoeringen(cd):
    """
    Function to return the content of a CD.

    :param cd: Id of the CD
    """
    uitvoeringen = Uitvoering.query.filter_by(cd_id=cd)
    return uitvoeringen

def get_last_uitvoering(cd):
    """
    Function to return the last uitvoering on a CD.

    :param cd: Id of the CD
    :return: uitvoering_dict - dictionary with uitvoering attributes volgnummer, uitvoerders_id, dirigent_id,
    kompositie_id and komponist_id.
    """
    uitvoering = Uitvoering.query.filter_by(cd_id=cd).order_by(Uitvoering.volgnummer.desc()).first()
    if uitvoering:
        if uitvoering.kompositie_id:
            kompositie = get_kompositie(uitvoering.kompositie_id)
        else:
            kompositie = None
        uitvoering_dict = dict(
            volgnummer=uitvoering.volgnummer or 0,
            uitvoerders_id=uitvoering.uitvoerders_id or -1,
            dirigent_id=uitvoering.dirigent_id or -1,
            kompositie_id=uitvoering.kompositie_id or -1,
            komponist_id=kompositie.komponist_id or -1,
            cd_id = cd
        )
    else:
        uitvoering_dict = dict(
            volgnummer=0,
            uitvoerders_id=-1,
            dirigent_id=-1,
            kompositie_id=-1,
            komponist_id=-1,
            cd_id=cd
        )
    return uitvoering_dict

def get_uitgever(nid):
    """
    Function to return uitgever for NID
    """
    return Uitgever.query.filter_by(id=nid).one()

def get_uitgever_pairs():
    """
    Function to return list of uitgevers in pairs uitgever.id, uitgever.naam. This can be used in a SelectField.
    """
    uitgevers = Uitgever.query.order_by(Uitgever.naam.asc())
    res = [(uitgever.id, uitgever.naam) for uitgever in uitgevers]
    return res

def get_uitgevers():
    """
    Function to return list of all Uitgevers.
    """
    return Uitgever.query

def get_uitvoerders_detail(uitvoerders_id):
    """
    Function to get uitvoerders record.

    :param uitvoerders_id: Id of the uitvoerders
    """
    uitvoerders = Uitvoerders.query.filter_by(id=uitvoerders_id).one()
    return uitvoerders

def get_uitvoerders_uitvoeringen(uitvoerders_id):
    """
    Function to get uitvoeringen for uitvoerders.

    :param uitvoerders_id: Id of the uitvoerders
    """
    return Uitvoering.query.filter_by(uitvoerders_id=uitvoerders_id)

def get_uitvoerders():
    """
    Function to return list of all Uitvoerders.
    """
    return Uitvoerders.query

def get_uitvoerders_pairs():
    """
    Function to return list of uitvoerders in pairs uitvoerders.id, uitvoerders.naam.
    This can be used in a SelectField.
    """
    uitvoerders = Uitvoerders.query.order_by(Uitvoerders.naam.asc())
    return [(uitvoerder.id, uitvoerder.naam) for uitvoerder in uitvoerders]

def get_uitvoeringen():
    """
    Function to get uitvoeringen.
    """
    return Uitvoering.query

def get_uitvoering(nid):
    """
    Functionto return the uitvoering as a record.
    """
    return Uitvoering.query.filter_by(id=nid).one()

def get_uitvoering_dict(nid):
    """
    Function to get a specific uitvoering. Result is returned as dictionary.

    :param nid: Id of the uitvoering required.
    :result: Dictionary with uitvoering
    """
    try:
        uitvoering = Uitvoering.query.filter_by(id=nid).one()
    except NoResultFound:
        return False
    else:
        uitvoering_dict = dict(
            volgnummer=uitvoering.volgnummer,
            uitvoerders_id=uitvoering.uitvoerders_id,
            dirigent_id=uitvoering.dirigent_id,
            kompositie_id=uitvoering.kompositie_id,
            komponist_id=uitvoering.kompositie.komponist_id,
            cd_id=uitvoering.cd_id
        )
        return uitvoering_dict
