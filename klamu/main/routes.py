import klamu.lib.db_model as ds
from flask import render_template, flash, redirect, url_for, request, session
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

@main.route('/cd/delete/<nid>', methods=['GET'])
@login_required
def delete_cd(nid):
    current_app.logger.debug(f"Referrer: {request.referrer}")
    res = Cd.delete(nid)
    if int(res['nid']) > 0:
        next_url = url_for('main.show_cd', nid=res['nid'])
    else:
        next_url = request.referrer
    flash(res['msg'], res['status'])
    return redirect(next_url)

@main.route('/dirigent/delete/<nid>', methods=['GET'])
@login_required
def delete_dirigent(nid):
    current_app.logger.debug(f"Referrer: {request.referrer}")
    res = Dirigent.delete(nid)
    if int(res['nid']) > 0:
        next_url = url_for('main.show_dirigent', nid=res['nid'])
    else:
        next_url = request.referrer
    flash(res['msg'], res['status'])
    return redirect(next_url)

@main.route('/komponist/delete/<nid>', methods=['GET'])
@login_required
def delete_komponist(nid):
    current_app.logger.debug(f"Referrer: {request.referrer}")
    res = Komponist.delete(nid)
    if int(res['nid']) > 0:
        next_url = url_for('main.show_komponist', nid=res['nid'])
    else:
        next_url = request.referrer
    flash(res['msg'], res['status'])
    return redirect(next_url)

@main.route('/uitgever/delete/<nid>', methods=['GET'])
@login_required
def delete_uitgever(nid):
    current_app.logger.debug(f"Referrer: {request.referrer}")
    res = Uitgever.delete(nid)
    if int(res['nid']) > 0:
        next_url = url_for('main.show_cds', nid=res['nid'])
    else:
        next_url = request.referrer
    flash(res['msg'], res['status'])
    return redirect(next_url)

@main.route('/uitvoerders/delete/<nid>', methods=['GET'])
@login_required
def delete_uitvoerders(nid):
    current_app.logger.debug(f"Referrer: {request.referrer}")
    res = Uitvoerders.delete(nid)
    if int(res['nid']) > 0:
        next_url = url_for('main.show_uitvoerders_uitvoeringen', nid=res['nid'])
    else:
        next_url = request.referrer
    flash(res['msg'], res['status'])
    return redirect(next_url)

@main.route('/komponist/selected', methods=['GET', 'POST'])
@login_required
def selected_komponist():
    komponist = request.get_json()
    print(komponist)
    komposities = get_komposities_for_komponist(komponist['komponist_id'])
    kompositie_list = [f"<option value=\"{k.id}\">{k.naam}</option>" for k in komposities.all()]
    return '<br>'.join(kompositie_list)

@main.route('/cd/<nid>')
def show_cd(nid):
    """
    Show content of a CD.

    :param nid: ID of the CD.
    """
    cd = ds.get_cd(nid)
    uitvoeringen = ds.get_cd_uitvoeringen(cd=nid)
    props = dict(
        cd_content_hdr=cd.titel,
        cd=cd,
        uitvoeringen=uitvoeringen
    )
    return render_template('cd_content.html', **props)

@main.route('/cds')
@main.route('/cds/<nid>')
def show_cds(nid=None):
    """
    Function to return CDs. If NID is specified, then CDs will be limited to uitgever with ID=NID.
    """
    cds = ds.get_cds(nid)
    props = dict(
        cd_list_hdr='Overzicht CDs',
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
    komponist = get_komponist(nid)
    uitvoeringen = get_komponist_uitvoeringen(nid)
    props = dict(
        hdr="{} {}".format(komponist.voornaam, komponist.naam),
        uitvoeringen=uitvoeringen
    )
    return render_template('uitvoeringen.html', **props)

@main.route('/komponisten')
def show_komponisten():
    komponisten = ds.get_komponisten()
    props = dict(
        komponisten_hdr='Overzicht Komponisten',
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

@main.route('/uitvoerders/update', methods=['GET', 'POST'])
@main.route('/uitvoerders/update/<nid>', methods=['GET', 'POST'])
@login_required
def update_uitvoerders(nid='-1'):
    if nid == '-1':
        nid = None
    current_app.logger.debug(f"Referrer: {request.referrer}")
    if url_for('main.update_uitvoering') in request.referrer:
        session['uitvoerders_referrer'] = request.referrer
        current_app.logger.debug(f"Referrer is toegevoegd.")
    form = forms.Uitvoerders()
    if request.method == "GET":
        if nid:
            # Update existing Uitvoerders
            this_uitvoerders = get_uitvoerders_detail(nid)
            form.uitvoerders.data = this_uitvoerders.naam
            props = dict(
                hdr="Uitvoerders Aanpassen",
                form=form,
                # uitvoerders=get_uitvoerders(),
                this_uitvoerders=this_uitvoerders.naam,
                uitvoeringen=get_uitvoerders_uitvoeringen(nid)
            )
        else:
            props = dict(
                hdr="Uitvoerders Toevoegen",
                form=form,
                uitvoerders=get_uitvoerders()
            )
        return render_template('uitvoerders_modify.html', **props)
    else:
        props = dict(
            naam=form.uitvoerders.data,
        )
        if nid:
            props['id'] = nid
        res = Uitvoerders.update(**props)
        flash(res['msg'], res['status'])
        session['uitvoerders_id'] = res['nid']
        next_url = session.pop('uitvoerders_referrer', url_for('main.show_uitvoerders', nid=res['nid']))
        return redirect(next_url)

@main.route('/cd/uitvoering/', methods=[])
@main.route('/cd/uitvoering/cd=<cid>', methods=['GET', 'POST'])
@main.route('/cd/uitvoering/uitvoering=<nid>', methods=['GET', 'POST'])
@login_required
def update_uitvoering(uitvoering=None, cid=None):
    if request.method == "GET":
        # If request to change CD
        if cid:
            cd = get_cd(cid)
            uitvoeringen = get_cd_uitvoeringen(cd=cid)
            this_uitvoering = get_last_uitvoering(cd=cid)
            this_uitvoering['volgnummer'] += 1
        elif uitvoering:
            this_uitvoering = get_uitvoering(uitvoering)
            cd = get_cd(this_uitvoering.cd_id)
            uitvoeringen = get_cd_uitvoeringen(cd=cd.id)
        else:
            flash('Onverwachte oproep', 'error')
            return redirect(request.referrer)
        form = forms.Uitvoering(
            volgnummer=this_uitvoering['volgnummer']+1,
            komponist=session.pop('komponist_id', this_uitvoering['komponist_id']),
            kompositie=session.pop('kompositie_id', -1),
            uitvoerders=session.pop('uitvoerders_id', this_uitvoering['uitvoerders_id']),
            dirigent=session.pop('dirigent_id', this_uitvoering['dirigent_id'])
        )
        res = ds.get_komponist_pairs()
        res.insert(0, (-1, '(kies komponist)'))
        form.komponist.choices = res
        res = ds.get_kompositie_pairs()
        res.insert(0, (-1, '(kies kompositie )'))
        form.kompositie.choices = res
        res = ds.get_uitvoerders_pairs()
        res.insert(0, (-1, '(geen uitvoerders)'))
        form.uitvoerders.choices = res
        res = ds.get_dirigent_pairs()
        res.insert(0, (-1, '(geen dirigent)'))
        form.dirigent.choices = res
        props = dict(
            cd_content_hdr=cd.titel,
            cd=cd,
            uitvoeringen=uitvoeringen,
            form=form
        )
        return render_template("uitvoering_modify.html", **props)
    else:
        form = forms.Uitvoering()
        if form.submit.data:
            props = dict(
                volgnummer=form.volgnummer.data,
                kompositie_id=form.kompositie.data,
                uitvoerders_id=form.uitvoerders.data,
                dirigent_id=form.dirigent.data
            )
            if uitvoering:
                this_uitvoering = get_uitvoering(uitvoering)
                props['id'] = uitvoering
                props['cd_id'] = this_uitvoering.cd_id
            elif cid:
                props['cd_id'] = cid
            res = Uitvoering.update(**props)
            flash(res['msg'], res['status'])
            session['uitvoerders_id'] = res['nid']
            next_url = session.pop('uitvoerders_referrer', url_for('main.show_uitvoerders', nid=res['nid']))
            return redirect(next_url)
        session['komponist_id'] = form.komponist.data
        session['kompositie_id'] = form.kompositie.data
        session['uitvoerders_id'] = form.uitvoerders.data
        session['dirigent_id'] = form.dirigent.data
        if form.komponist_mod.data:
            return redirect(url_for('main.update_komponist', nid=session['komponist_id']))
        elif form.uitvoerders_mod.data:
            return redirect(url_for('main.update_uitvoerders', nid=session['uitvoerders_id']))
        elif form.dirigent_mod.data:
            return redirect(url_for('main.update_dirigent', nid=session['dirigent_id']))
        elif form.kompositie_mod.data:
            return redirect(url_for('main.update_kompositie', nid=session['kompositie_id']))
        else:
            msg = "Invalid request"
            flash(msg, "error")
            current_app.logger.error(msg)
            return redirect(url_for("main.show_cds"))


@main.route('/cd/update', methods=['GET', 'POST'])
@main.route('/cd/update/<nid>', methods=['GET', 'POST'])
@login_required
def update_cd(nid=None):
    if request.method == "GET":
        # If referrer is update_uitgever, set uitgever_id.
        uitgever_id = session.pop('uitgever_id', None)
        if uitgever_id:
            form = forms.Cd(uitgever=uitgever_id)
        elif not nid:
            form = forms.Cd()
        if nid:
            # Update existing CD - Keep on using original titel and identificatie after changing Uitgever.
            cd = get_cd(nid)
            if not uitgever_id:
                if cd.uitgever_id:
                    form = forms.Cd(uitgever=cd.uitgever_id)
                else:
                    form = forms.Cd()
            form.titel.data = cd.titel
            form.identificatie.data = cd.identificatie
            session.pop('titel', None)
            session.pop('identificatie', None)
        else:
            # In case of new CD, remember Titel and Identificatie from before changing Uitgever.
            form.titel.data = session.pop('titel', None)
            form.identificatie.data = session.pop('identificatie', None)
        uitgevers = ds.get_uitgever_pairs()
        uitgevers.insert(0, (-1, '(geen uitgever)'))
        form.uitgever.choices = uitgevers
        cds = ds.get_cds(uitgever_id)
        props = dict(
            form=form,
            cd_list_hdr='Overzicht CDs',
            cds=cds
        )
        if nid:
            props['uitvoeringen'] = get_cd_uitvoeringen(nid)
            props['cd'] = get_cd(nid)
        return render_template('cd_modify.html', **props)
    else:
        form = forms.Cd()
        if form.uitgever_mod.data:
            # Request to Update Uitgever
            session['titel'] = form.titel.data
            session['identificatie'] = form.identificatie.data
            uitgever_id = form.uitgever.data
            return redirect(url_for('main.update_uitgever', nid=uitgever_id))
        else:
            # Submit Form
            props = dict(
                titel=form.titel.data,
                identificatie=form.identificatie.data,
                uitgever_id=form.uitgever.data
            )
            if nid:
                props['id'] = nid
            nid = Cd.update(**props)
            return redirect(url_for('main.show_cd', nid=nid))

@main.route('/dirigent/update', methods=['GET', 'POST'])
@main.route('/dirigent/update/<nid>', methods=['GET', 'POST'])
@login_required
def update_dirigent(nid='-1'):
    if nid == '-1':
        nid = None
    current_app.logger.debug(f"Referrer: {request.referrer}")
    if url_for('main.update_uitvoering') in request.referrer:
        session['dirigent_referrer'] = request.referrer
        current_app.logger.debug(f"Referrer is toegevoegd.")
    form = forms.Dirigent()
    if request.method == "GET":
        if nid:
            # Update existing Komponist
            dirigent = get_dirigent(nid)
            form.naam.data = dirigent.naam
            form.voornaam.data = dirigent.voornaam
            props = dict(
                hdr="Dirigent Aanpassen",
                form=form,
                dirigent=dirigent,
                uitvoeringen=get_dirigent_uitvoeringen(nid)
            )
        else:
            props = dict(
                hdr="Dirigent Toevoegen",
                form=form,
                dirigenten=get_dirigenten()
            )
        return render_template('dirigent_modify.html', **props)
    else:
        props = dict(
            naam=form.naam.data,
            voornaam = form.voornaam.data
        )
        if nid:
            props['id'] = nid
        res = Dirigent.update(**props)
        flash(res['msg'], res['status'])
        session['dirigent_id'] = res['nid']
        next_url = session.pop('dirigent_referrer', url_for('main.show_dirigenten'))
        return redirect(next_url)

@main.route('/komponist/update', methods=['GET', 'POST'])
@main.route('/komponist/update/<nid>', methods=['GET', 'POST'])
@login_required
def update_komponist(nid='-1'):
    if nid == '-1':
        nid = None
    current_app.logger.debug(f"Referrer: {request.referrer}")
    # if url_for('main.update_uitvoering') in request.referrer:
    session['komponist_referrer'] = request.referrer
    current_app.logger.debug(f"Referrer is toegevoegd.")
    form = forms.Komponist()
    if request.method == "GET":
        if nid:
            # Update existing Komponist
            komponist = get_komponist(nid)
            form.naam.data = komponist.naam
            form.voornaam.data = komponist.voornaam
            props = dict(
                hdr="Komponist Aanpassen",
                form=form,
                # komponisten=get_komponisten(),
                komponist=komponist,
                uitvoeringen=get_komponist_uitvoeringen(nid)
            )
        else:
            props = dict(
                hdr="Komponist Toevoegen",
                form=form,
                komponisten=get_komponisten()
            )
        return render_template('komponist_modify.html', **props)
    else:
        props = dict(
            naam=form.naam.data,
            voornaam = form.voornaam.data
        )
        if nid:
            props['id'] = nid
        res = Komponist.update(**props)
        flash(res['msg'], res['status'])
        session['komponist_id'] = res['nid']
        # Remove kompositie if it was set
        session.pop('kompositie_id', None)
        next_url = session.pop('komponist_referrer', url_for('main.show_komponisten', nid=res['nid']))
        return redirect(next_url)

@main.route('/kompositie/update', methods=['GET', 'POST'])
@main.route('/kompositie/update/<nid>', methods=['GET', 'POST'])
@login_required
def update_kompositie(nid='-1'):
    if nid == '-1':
        nid = None
    session['kompositie_referrer'] = request.referrer
    current_app.logger.debug(f"Referrer {request.referrer} is toegevoegd.")
    if request.method == "GET":
        if nid:
            # Update existing Kompositie
            hdr = "Kompositie Aanpassen"
            kompositie = get_kompositie(nid)
            komponist = get_komponist(kompositie.komponist_id)
            form = forms.Kompositie(komponist=komponist.id)
            form.naam.data = kompositie.naam
            uitvoeringen = get_kompositie_uitvoeringen(nid)
            uitvoeringen_hdr = kompositie.naam
        elif 'komponist_id' in session:
            # Add kompositie for komponist
            hdr = "Kompositie Toevoegen"
            komponist_id = session['komponist_id']
            komponist = get_komponist(komponist_id)
            form = forms.Kompositie(komponist=komponist_id)
            uitvoeringen = get_komponist_uitvoeringen(komponist_id)
            uitvoeringen_hdr = f"{komponist.voornaam} {komponist.naam}"
        else:
            # Set komponist and kompositie
            hdr = "Kompositie Toevoegen"
            form = forms.Kompositie(komponist=-1)
            # komponisten = get_komponisten()
            uitvoeringen_hdr = None
        komponisten = ds.get_komponist_pairs()
        komponisten.insert(0, (-1, '(geen komponist)'))
        form.komponist.choices = komponisten
        komposities = get_kompositie_pairs()
        # komposities.insert(0, (-1, '(geen kompositie)'))
        form.naam.choices = komposities
        props = dict(
            hdr=hdr,
            form=form
        )
        if uitvoeringen_hdr:
            props['uitvoeringen'] = uitvoeringen
            props['uitvoeringen_hdr'] = uitvoeringen_hdr
        else:
            props['komponisten'] = komponisten
        return render_template('kompositie_modify.html', **props)
    else:
        form = forms.Kompositie()
        props = dict(
            naam=form.naam.data,
            komponist_id=form.komponist.data
        )
        if nid:
            props['id'] = nid
        res = Kompositie.update(**props)
        flash(res['msg'], res['status'])
        session['kompositie_id'] = res['nid']
        next_url = session.pop('kompositie_referrer', url_for('main.show_kompositie', nid=res['nid']))
        return redirect(next_url)


@main.route('/uitgever/update', methods=['GET', 'POST'])
@main.route('/uitgever/update/<nid>', methods=['GET', 'POST'])
@login_required
def update_uitgever(nid='-1'):
    if nid == '-1':
        nid = None
    current_app.logger.debug(f"Referrer: {request.referrer}")
    if url_for('main.update_cd') in request.referrer:
        session['uitgever_referrer'] = request.referrer
    if request.method == "GET":
        form = forms.Uitgever()
        props = dict(
            hdr='Uitgever Toevoegen',
            form=form
        )
        if nid:
            # Update existing Uitgever
            uitgever = get_uitgever(nid)
            form.uitgever.data = uitgever.naam
            props['cds'] = get_cds(nid)
            props['uitgever'] = uitgever.naam
        else:
            props['uitgevers'] = get_uitgevers()
        return render_template('uitgever_modify.html', **props)
    else:
        form = forms.Uitgever()
        props = dict(
            naam=form.uitgever.data
        )
        if nid:
            props['id'] = nid
        res = Uitgever.update(**props)
        flash(res['msg'], res['status'])
        session['uitgever_id'] = res['nid']
        next_url = session.pop('uitgever_referrer', url_for('main.show_cds', nid=res['nid']))
        return redirect(next_url)

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
