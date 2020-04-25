import klamu.lib.db_model as ds
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .forms import *
from . import main
from klamu.lib.db_model import *


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Login not successful', "error")
            return redirect(url_for('main.login', **request.args))
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('login.html', form=form, hdr='Login')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/pwdupdate', methods=['GET', 'POST'])
@login_required
def pwd_update():
    form = PwdUpdate()
    if form.validate_on_submit():
        user = ds.load_user(current_user.get_id())
        if user is None or not user.verify_password(form.current_pwd.data):
            flash('Password update not successful', 'error')
            return redirect(url_for('main.pwd_update'))
        # User and password is OK, so update the password
        user.set_password(form.new_pwd.data)
        flash('Password changed!', 'info')
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form, hdr='Change Password')


@main.route('/')
@main.route('/index')
def index():
    return render_template("index.html")


@main.errorhandler(404)
def not_found(e):
    return render_template("404.html", err=e)

@main.route('/cd/<nid>')
def show_cd(nid):
    """
    Show content of a CD.

    :param nid: ID of the CD.
    """
    cd = ds.get_cd(nid)
    uitvoeringen = ds.get_cd_uitvoeringen(cd=nid)
    props = dict(
        hdr=cd.titel,
        cd=cd,
        uitvoeringen=uitvoeringen.order_by(Uitvoering.volgnummer)
    )
    return render_template('cd_content.html', **props)

@main.route('/cds')
def show_cds():
    cds = ds.get_cds()
    props = dict(
        hdr='Overzicht CDs',
        cds=cds.order_by(Cd.titel)
    )
    return render_template('cds.html', **props)

@main.route('/komponist/<nid>')
def show_komponist(nid):
    komponist = ds.get_komponist(nid)
    props = dict(
        hdr="{} {}".format(komponist.voornaam, komponist.naam),
        komponist=komponist
    )
    return render_template('komponist.html', **props)

@main.route('/komponisten')
def show_komponisten():
    komponisten = ds.get_komponisten()
    props = dict(
        hdr='Overzicht Komponisten',
        komponisten=komponisten.order_by(Komponist.naam)
    )
    return render_template('komponisten.html', **props)

@main.route('/kompositie/<nid>')
def show_kompositie(nid):
    kompositie = ds.get_kompositie(nid)
    props = dict(
        hdr="{} - {} {}".format(kompositie.naam, kompositie.komponist.voornaam, kompositie.komponist.naam),
        kompositie=kompositie
    )
    return render_template('kompositie.html', **props)

@main.route('/komposities')
def show_komposities():
    komposities = ds.get_komposities()
    props = dict(
        hdr='Overzicht Komposities',
        komposities=komposities.order_by(Kompositie.naam)
    )
    return render_template('komposities.html', **props)

@main.route('/uitvoerders/<nid>')
def show_uitvoerders_uitvoeringen(nid):
    uitvoerders = ds.get_uitvoerders_detail(nid)
    uitvoeringen = ds.get_uitvoerders_uitvoeringen(nid)
    props = dict(
        hdr=uitvoerders.naam,
        uitvoeringen=uitvoeringen
    )
    return render_template('uitvoerders_uitvoeringen.html', **props)

@main.route('/uitvoerders')
def show_uitvoerders():
    uitvoerders = ds.get_uitvoerders()
    props = dict(
        hdr='Overzicht Uitvoerders',
        uitvoerders=uitvoerders
    )
    return render_template('uitvoerders.html', **props)
