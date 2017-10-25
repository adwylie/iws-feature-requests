import datetime
import textwrap
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy

from iws_fr import app
db = SQLAlchemy(app)


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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    identifier = db.Column(db.Integer, default=next_identifier, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Integer, default=next_priority, nullable=False)
    target_date = db.Column(db.DateTime, nullable=False)
    created = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    user = db.relationship('User', backref=db.backref('feature_requests'), lazy=True)
    client = db.relationship('Client', backref=db.backref('feature_requests'), lazy=True)
    product_areas = db.relationship(
        'ProductArea',
        secondary=fr_pa_map,
        lazy='subquery',
        backref=db.backref('feature_requests', lazy=True)
    )

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
    # Determine the action to take. Either:
    # 1. The FR exists & is being moved to a location with an existing FR.
    #  - Find the old and new locations.
    #  - Work from the new location to the old, recursively moving FRs.
    #  - We can stop upon reaching the old location or at an empty location.

    # 2. The FR is new and is being added in a location with an existing FR.
    #  - Work from the new location to +infinity, recursively moving FRs.
    #  - This is a subset of the previous case.

    # 3. In all other cases the new location doesn't contain an existing FR.
    #  - Nothing needs to be done.

    def next_priority(current, target):
        """Return a priority value which is 1 unit closer to the target.

        An omitted (or None) target assumes shifting priorities down (to larger
        values).

        """
        if target is None:
            return current + 1
        else:
            return current + ((target - current) // abs(target - current))

    def update_priority(current_priority, end_priority, client_id):
        """Recursively update the priorities of (adjacent) FRs."""
        duplicate = FeatureRequest.query.filter_by(
            client_id=client_id,
            priority=current_priority
        ).first()

        if duplicate and current_priority != end_priority:
            updated_priority = next_priority(current_priority, end_priority)

            # Update the next FR first.
            update_priority(updated_priority, end_priority, client_id)

            # Then change the current FR.
            duplicate.priority = updated_priority
            session.add(duplicate)

    # Get all frs that could possibly need to be changed.
    frs = sorted(
        [x for x in session.new | session.dirty if isinstance(x, FeatureRequest)],
        key=lambda fr: fr.priority,
        reverse=True
    )

    # Iterate from lowest priority to highest (highest value to lowest),
    # move all priority objects recursively when a duplicate is found.
    for fr in frs:
        session.expunge(fr)
        exists = FeatureRequest.query.filter_by(id=fr.id).first()

        start_priority = fr.priority
        end_priority = None if not exists else exists.priority

        session.merge(fr)
        update_priority(start_priority, end_priority, fr.client_id)


class Comment(db.Model):
    """Comment on a feature request."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feature_request_id = db.Column(db.Integer, db.ForeignKey('feature_request.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    user = db.relationship('User', backref=db.backref('comments'), lazy=True)
    feature_request = db.relationship('FeatureRequest', backref=db.backref('comments'), lazy=True)

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
        return '<User {}>'.format(self.first_name + ' ' + self.last_name)


class ProductArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)

    def __str__(self):
        return '<ProductArea {}>'.format(self.name)
