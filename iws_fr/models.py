import datetime
import textwrap
import flask_restless
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from .settings import app
from .settings import db


# Many-to-many relation (through table) between FeatureRequest and ProductArea.
fr_pa_map = db.Table(
    'fr_pa_map',
    db.Column('feature_request_id', db.Integer, db.ForeignKey('feature_request.id'), primary_key=True),
    db.Column('product_area_id', db.Integer, db.ForeignKey('product_area.id'), primary_key=True)
)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)

    def __str__(self):
        return '<Client {}>'.format(self.name)


class FeatureRequest(db.Model):
    """Represents a submitted feature request (FR).

    The FR is submitted by a user referencing a particular client's software.

    """
    def next_identifier(context):
        """Return a new default identifier for a FR with respect to a client."""
        max_identifier = db.session.query(
            func.max(FeatureRequest.identifier)
        ).filter(
            FeatureRequest.client_id == context.current_parameters['client_id']
        ).scalar()

        next_identifier = 1 if max_identifier is None else max_identifier + 1

        return next_identifier

    def next_priority(context):
        """Return a new default priority for a FR with respect to a client.

        Smaller-valued priorities are 'higher', so return the maximum value
        plus one -- the lowest priority.

        """
        max_priority = db.session.query(
            func.max(FeatureRequest.priority)
        ).filter(
            FeatureRequest.client_id == context.current_parameters['client_id']
        ).scalar()

        next_priority = 1 if max_priority is None else max_priority + 1

        return next_priority

    id = db.Column(db.Integer, primary_key=True)

    # Each FR is created by a user in reference to a certain client's software.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    identifier = db.Column(db.Integer, default=next_identifier, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Integer, default=next_priority, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    product_areas = db.relationship(
        'ProductArea',
        secondary=fr_pa_map,
        lazy='subquery',
        backref=db.backref('feature_requests', lazy=True)
    )
    created = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    user = db.relationship('User', backref=db.backref('comments'), lazy=True)
    client = db.relationship('Client', backref=db.backref('feature_requests'), lazy=True)

    __table_args__ = (
        db.CheckConstraint(priority > 0, name='positive_priority'),
        db.UniqueConstraint('client_id', 'identifier', name='unique_client_identifiers'),
        # db.UniqueConstraint('client_id', 'priority', name='unique_client_priorities')
    )

    @validates('target_date')
    def validate_future_date(self, key, date):
        """Ensure the given date(s) occur in the future."""
        if date <= datetime.datetime.now():
            raise ValueError(
                'Value for field {} must occur in the future.'.format(key)
            )

        return date

    def __str__(self):
        return '<FeatureRequest {}>'.format(self.title)


@event.listens_for(db.session, 'before_flush')
def reorder_priorities(session, flush_context, instances):
    """Check (and update) FR priorities before changes are committed."""
    # TODO: Multiple overlapping re-orderings can fail, as duplicated
    # TODO: priorities are not updated more than once (session.add constraint).
    # TODO: Will not be an issue unless executing batch updates.
    # Get all frs that could possibly need to be changed.
    frs = sorted(
        [x for x in session.new | session.dirty if isinstance(x, FeatureRequest)],
        key=lambda fr: fr.priority,
        reverse=True
    )

    def update_priority(fr, client_id, priority):
        """Recursively update the priorities of (adjacent) FRs."""
        duplicate = FeatureRequest.query.filter_by(
            client_id=client_id,
            priority=priority
        ).first()

        # Protect against overrunning what should be a closed loop
        # (where an updated FR takes the place of the initially moved FR).
        if duplicate and duplicate.id != fr.id:
            # Update the next FR (with lower priority) first.
            update_priority(fr, client_id, priority + 1)

            # Change the current FR after the lower priority FR is updated.
            duplicate.priority = priority + 1
            session.add(duplicate)

    # Iterate from lowest priority to highest (highest value to lowest),
    # move all priority objects up recursively when a duplicate is found.
    for fr in frs:
        update_priority(fr, fr.client_id, fr.priority)


class Comment(db.Model):
    """Comment on a feature request."""
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('user_comments'), lazy=True)

    feature_request_id = db.Column(db.Integer, db.ForeignKey('feature_request.id'), nullable=False)
    feature_request = db.relationship('FeatureRequest', backref=db.backref('feature_comments'), lazy=True)

    text = db.Column(db.Text, nullable=False)
    created = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    def __str__(self):
        # String representation includes user name, feature request number,
        # and a short summary of the comment itself.
        return '<Comment {}, FR#{}: {}'.format(
            self.user,
            self.feature_request_id,
            textwrap.wrap(self.text, width=10)[0]
        )


class User(db.Model):
    """User of the system for authentication/authorization purposes."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)

    @hybrid_property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return '<User {}>'.format(self.full_name)


class ProductArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)

    def __str__(self):
        return '<ProductArea {}>'.format(self.name)


# Set up restful api.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Comment, methods=['GET', 'POST', 'DELETE'])
manager.create_api(FeatureRequest, methods=['GET', 'POST', 'DELETE'])
