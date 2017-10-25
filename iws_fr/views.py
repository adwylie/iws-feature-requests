from flask import render_template
import flask_restless

from iws_fr import app
from .models import db
from .models import (Client, FeatureRequest, Comment, User, ProductArea)


# TODO: Model forms (wtforms)?
@app.route('/')
def main():
    return render_template('feature_requests.html')


# Set up restful api.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(Client, methods=['GET', 'POST', 'DELETE'])
manager.create_api(FeatureRequest, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
manager.create_api(Comment, methods=['GET', 'POST', 'DELETE'])
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])
manager.create_api(ProductArea, methods=['GET', 'POST', 'DELETE'])
