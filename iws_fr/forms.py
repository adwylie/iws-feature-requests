from flask_wtf import FlaskForm, RecaptchaField
from wtforms import DateTimeField, IntegerField, StringField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from .models import Client, User


def user_choices():
    return User.query.all()


def client_choices():
    return Client.query.all()


class FeatureRequestForm(FlaskForm):
    # TODO: Allow selection of product areas.
    user = QuerySelectField('User', validators=[DataRequired()], query_factory=user_choices, get_label='full_name')
    client = QuerySelectField('Client', validators=[DataRequired()], query_factory=client_choices, get_label='name')
    title = StringField('Title', validators=[DataRequired(), Length(max=60)])
    description = TextAreaField('Description', validators=[Optional()])
    # TODO: make description required (update tests, model, form).
    # TODO: optional priority, will be filled in if not provided.
    priority = IntegerField('Priority', validators=[DataRequired(), NumberRange(min=1)])
    target_date = DateTimeField('Target Date', validators=[DataRequired()])
    recaptcha = RecaptchaField()
