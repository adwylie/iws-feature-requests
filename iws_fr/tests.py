import os
import unittest
import tempfile
from flask_fixtures import FixturesMixin

from .settings import app
from .settings import db
from .models import (Client, ProductArea, User)

# Disable info logging in flask_fixtures library.
import logging
logging.disable(logging.INFO)


class FlaskTestCase(unittest.TestCase, FixturesMixin):
    fixtures = ['clients.json', 'productareas.json', 'users.json']
    app, db = app, db  # Required setup for fixtures to work.

    def setUp(self):
        app.testing = True
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.test_client()

        db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    # Tests.
    def test_default_data(self):
        """Ensure fixtures can be loaded."""
        clients = Client.query.all()
        product_areas = ProductArea.query.all()
        users = User.query.all()

        assert len(clients) == Client.query.count() == 3
        assert len(product_areas) == ProductArea.query.count() == 4
        assert len(users) == User.query.count() == 7

    def test_feature_request_priority_range(self):
        # DB-level FR positive priority constraint
        pass

    def test_feature_request_priority_duplication(self):
        # DB-level FR unique priority constraint.
        pass

    def test_feature_request_priority_creation(self):
        # App-level FR priority inserts.
        pass

    def test_feature_request_target_date_default(self):
        # App-level FR target_date >= today.
        pass

    def test_feature_request_identifier_increment(self):
        # App-level FR identifier auto-set on save (wrt/ client).
        pass

    def test_comment_created_default(self):
        """Test that the Comment.created field is set by default."""
        pass

    def test_user_full_name(self):
        """Test that the User.full_name property works."""
        bill_id = 4
        bill_full_name = 'Bill Lumbergh'

        bill = User.query.get(bill_id)

        assert bill
        assert bill.full_name == bill_full_name
        assert bill == User.query.filter_by(full_name=bill_full_name).one()

    # TODO: Test restful api available methods?


if '__main__' == __name__:
    unittest.main()
