# TODO: Is the request import needed for flask-wtf
from flask import render_template, request
import flask_restless

from iws_fr import app
from .models import db
from .models import (Client, FeatureRequest, Comment, User, ProductArea)
from .forms import FeatureRequestForm


# TODO: Model forms (wtforms)?
@app.route('/')
def main():
    return render_template('list_frs.html')


@app.route('/new/', methods=('GET', 'POST'))
def new():
    messages = []

    form = FeatureRequestForm()

    if form.validate_on_submit():
        print('yay!')
        # Save the form.
        # Redirect to view the newly-created feature request.

    return render_template('new_fr.html', form=form, messages=messages)


@app.route('/view/<int:id>/')
def view(id):
    feature_request = FeatureRequest.query.filter_by(id=id).first()
    comments = Comment.query.filter_by(feature_request_id=id).order_by(Comment.created)

    return render_template(
        'view_fr.html',
        feature_request=feature_request,
        comments=comments
    )


@app.route('/edit/<int:id>/')
def edit(id):
    return render_template('edit_fr.html')


# Set up restful api.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(Client, methods=['GET', 'POST', 'DELETE'])
manager.create_api(FeatureRequest, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
manager.create_api(Comment, methods=['GET', 'POST', 'DELETE'])
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])
manager.create_api(ProductArea, methods=['GET', 'POST', 'DELETE'])
