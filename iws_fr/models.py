import datetime
import textwrap
from flask_sqlalchemy import SQLAlchemy
from .views import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TODO: tests
# TODO: model forms?, templates?
# TODO: settings.py?

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
    id = db.Column(db.Integer, primary_key=True)

    # Each feature request is created by a user on behalf of a client.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments'), lazy=True)

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('feature_requests'), lazy=True)

    # Identifier is a per-client feature request id.
    identifier = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Integer, nullable=False)  # TODO: update priorities on save
    target_date = db.Column(db.Date, nullable=False)  # TODO: must be >= today
    product_areas = db.relationship(
        'ProductArea',
        secondary=fr_pa_map,
        lazy='subquery',
        backref=db.backref('feature_requests', lazy=True)
    )

    # TODO: Test constraints.
    __table_args__ = (
        db.CheckConstraint(priority > 0, name='positive_priority'),
        db.UniqueConstraint('client_id', 'priority', name='unique_client_priorities')
    )

    def __str__(self):
        return '<FeatureRequest {}>'.format(self.title)


class Comment(db.Model):
    """Comment on a feature request."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(  # TODO: TEST default datetime value.
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments'), lazy=True)

    feature_request_id = db.Column(db.Integer, db.ForeignKey('feature_request.id'), nullable=False)
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

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return '<User {}>'.format(self.full_name)


class ProductArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)

    def __str__(self):
        return '<ProductArea {}>'.format(self.name)
