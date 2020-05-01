import klamu.lib.db_model as ds
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from . import forms
from . import main
from klamu.lib.db_model import *


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.Login()
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
    form = forms.PwdUpdate()
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
def page_not_found(e):
    return render_template("404.html", err=e)

@main.route('/uitgever/update')
@login_required
def uitgever_update():
    flash(request.referrer, 'info')
    return redirect(url_for('main.index'))

@main.route('/cd/update', methods=['GET', 'POST'])
@main.route('/cd/update/<nid>', methods=['GET', 'POST'])
@login_required
def cd_update(nid=None):
    if request.method == "GET":
        if nid:
            # Update existing CD
            cd = get_cd(nid)
            if cd.uitgever_id:
                form = forms.Cd(uitgever=cd.uitgever_id)
            else:
                form = forms.Cd()
            form.titel.data = cd.titel
            form.identificatie.data = cd.identificatie
        else:
            form = forms.Cd()
        uitgevers = ds.get_uitgever_pairs()
        uitgevers.insert(0, (-1, '(geen uitgever)'))
        form.uitgever.choices = uitgevers
        props = dict(
            form=form
        )
        return render_template('cd_modify.html', **props)
    else:
        form = forms.Cd()
        props = dict(
            titel=form.titel.data,
            identificatie=form.identificatie.data,
            uitgever_id=form.uitgever.data
        )
        if props['uitgever_id'] == -1:
            props['uitgever_id'] = None
        if nid:
            props['id'] = nid
        nid = Cd.update(**props)
        return redirect(url_for('main.show_cd', nid=nid))

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
        uitvoeringen=uitvoeringen
    )
    return render_template('cd_content.html', **props)

@main.route('/cds')
@main.route('/cds/<nid>')
def show_cds(nid=None):
    cds = ds.get_cds(nid)
    props = dict(
        hdr='Overzicht CDs',
        cds=cds
    )
    return render_template('cds.html', **props)

@main.route('/dirigent/<nid>')
def show_dirigent(nid):
    dirigent = ds.get_dirigent(nid)
    uitvoeringen = ds.get_dirigent_uitvoeringen(nid)
    props = dict(
        hdr="{} {}".format(dirigent.voornaam, dirigent.naam),
        uitvoeringen=uitvoeringen
    )
    return render_template('uitvoeringen.html', **props)

@main.route('/dirigenten')
def show_dirigenten():
    dirigenten = ds.get_dirigenten()
    props = dict(
        hdr='Overzicht Dirigenten',
        dirigenten=dirigenten
    )
    return render_template('dirigenten.html', **props)

@main.route('/komponist/<nid>')
def show_komponist(nid):
    komponist = ds.get_komponist(nid)
    uitvoeringen = ds.get_komponist_uitvoeringen(nid)
    props = dict(
        hdr="{} {}".format(komponist.voornaam, komponist.naam),
        uitvoeringen=uitvoeringen
    )
    return render_template('uitvoeringen.html', **props)

@main.route('/komponisten')
def show_komponisten():
    komponisten = ds.get_komponisten()
    props = dict(
        hdr='Overzicht Komponisten',
        komponisten=komponisten
    )
    return render_template('komponisten.html', **props)

@main.route('/kompositie/<nid>')
def show_kompositie(nid):
    kompositie = ds.get_kompositie(nid)
    uitvoeringen = ds.get_kompositie_uitvoeringen(nid)
    props = dict(
        hdr="{} - {} {}".format(kompositie.naam, kompositie.komponist.voornaam, kompositie.komponist.naam),
        uitvoeringen=uitvoeringen
    )
    return render_template('uitvoeringen.html', **props)

@main.route('/komposities')
def show_komposities():
    komposities = ds.get_komposities()
    props = dict(
        hdr='Overzicht Komposities',
        komposities=komposities
    )
    return render_template('komposities.html', **props)

@main.route('/uitgevers')
def show_uitgevers():
    uitgevers = ds.get_uitgevers()
    props = dict(
        hdr='Overzicht Uitgevers',
        uitgevers=uitgevers
    )
    return render_template('uitgevers.html', **props)

@main.route('/uitvoerders/<nid>')
def show_uitvoerders_uitvoeringen(nid):
    uitvoerders = ds.get_uitvoerders_detail(nid)
    uitvoeringen = ds.get_uitvoerders_uitvoeringen(nid)
    props = dict(
        hdr=uitvoerders.naam,
        uitvoeringen=uitvoeringen
    )
    return render_template('uitvoeringen.html', **props)

@main.route('/uitvoerders')
def show_uitvoerders():
    uitvoerders = ds.get_uitvoerders()
    props = dict(
        hdr='Overzicht Uitvoerders',
        uitvoerders=uitvoerders
    )
    return render_template('uitvoerders.html', **props)

@main.route('/uitvoeringen')
def show_uitvoeringen():
    uitvoeringen = ds.get_uitvoeringen()
    props = dict(
        hdr='Overzicht Uitvoeringen',
        uitvoeringen=uitvoeringen
    )
    return render_template('uitvoeringen.html', **props)

@main.route('/register')
def register():
    ds.User.register('christien', 'christien')
    return redirect('main.index')
