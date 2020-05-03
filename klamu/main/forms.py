from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField
import wtforms.validators as wtv

from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class Login(Form):
    username = StringField('Username', validators=[wtv.InputRequired(), wtv.Length(1, 16)])
    password = PasswordField('Password', validators=[wtv.InputRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('OK')


class PwdUpdate(Form):
    current_pwd = PasswordField('Current Password', validators=[wtv.InputRequired()])
    new_pwd = PasswordField('New Password', validators=[wtv.InputRequired(),
                                                        wtv.EqualTo('confirm_pwd', message='Passwords must match'),
                                                        wtv.Length(min=4, message='Minimum length is %(min)d')])
    confirm_pwd = PasswordField('Re-Enter New Password')
    submit = SubmitField('Change')


class Search(Form):
    search = StringField('Search', validators=[wtv.InputRequired()])
    submit = SubmitField('Go!')

class Cd(Form):
    titel = StringField('Titel', validators=[wtv.InputRequired()], render_kw={"placeholder":'Titel van de CD'})
    identificatie = StringField('Identificatie', render_kw={"placeholder":'Bijkomende informatie'})
    uitgever = SelectField('Uitgever', coerce=str)
    submit = SubmitField('OK')
    uitgever_mod = SubmitField('Uitgever Aanpassen')

class Uitgever(Form):
    uitgever = StringField('Naam', validators=[wtv.InputRequired()])
    submit = SubmitField('OK')

class Uitvoering(Form):
    volgnummer = IntegerField('Volgnummer')
    komponist = SelectField('Komponist', coerce=str)
    kompositie = SelectField('Kompositie', coerce=str)
    uitvoerders = SelectField('Uitvoerders', coerce=str)
    dirigent = SelectField('Dirigent', coerce=str)
    submit = SubmitField('OK')
    komponist_mod = SubmitField('Komponist Aanpassen')
    kompositie_mod = SubmitField('Kompositie Aanpassen')
    uitvoerders_mod = SubmitField('Uitvoerders Aanpassen')
    dirigent_mod = SubmitField('Dirigent Aanpassen')
