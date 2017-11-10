from flask import render_template, redirect, url_for
import flask_restless

from iws_fr import app
from .models import db
from .models import (Client, FeatureRequest, Comment, User, ProductArea)
from .forms import FeatureRequestForm


@app.route('/')
def main():
    return render_template('list_frs.html')


@app.route('/new/', methods=('GET', 'POST'))
@app.route('/edit/<int:id>/', methods=('GET', 'POST'))
def edit(id=None):

    if id:
        fr = FeatureRequest.query.filter_by(id=id).first() or FeatureRequest()
        form = FeatureRequestForm(obj=fr)
        title = "Editing '{}'".format(fr.title)
        action = 'edit'
    else:
        fr = FeatureRequest()
        form = FeatureRequestForm()
        title = 'Creating a New Feature Request'
        action = 'create'

    if form.validate_on_submit():
        try:
            form.populate_obj(fr)
        except ValueError as error:
            # TODO: Is there a better way of passing error up from the model?
            form.errors['target_date'] = [str(error)]
        else:
            db.session.add(fr)
            db.session.commit()

            # TODO:
            # Feature request id isn't populated after commit for some
            # reason, so we'll just redirect to main page.
            return redirect(url_for('main'))

    return render_template(
        'edit_fr.html', form=form, title=title, action=action)


@app.route('/delete/<int:id>/')
def delete(id):
    fr = FeatureRequest.query.filter_by(id=id).first()
    if fr:
        db.session.delete(fr)
        db.session.commit()

    return redirect(url_for('main'))


@app.route('/view/<int:id>/')
def view(id):
    feature_request = FeatureRequest.query.filter_by(id=id).first()
    comments = Comment.query.filter_by(feature_request_id=id).order_by(Comment.created)

    return render_template(
        'view_fr.html',
        feature_request=feature_request,
        comments=comments
    )


# Set up restful api.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(Client, methods=['GET', 'POST', 'DELETE'])
manager.create_api(FeatureRequest, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
manager.create_api(Comment, methods=['GET', 'POST', 'DELETE'])
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])
manager.create_api(ProductArea, methods=['GET', 'POST', 'DELETE'])
