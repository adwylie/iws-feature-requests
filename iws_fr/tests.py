import datetime
import os
import unittest
import tempfile
from flask_fixtures import FixturesMixin

from .settings import app
from .settings import db
from .models import (Client, Comment, FeatureRequest, ProductArea, User)

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

    def test_feature_request_comment_created_default(self):
        """Test that the FeatureRequest and Comment 'created' fields are set."""
        # Michael Bolton creates first FR for Initech, no product areas.
        fr = FeatureRequest(
            user_id=3,
            client_id=3,
            identifier=1,
            title='Convert 2-digit dates to 4-digit.',
            description='Prepare for Y2K by updating date storage format',
            priority=1,
            target_date=datetime.datetime(1999, 12, 31, 23, 59, 59)
        )

        # Bill Lumbergh replies in his typical way.
        comment = Comment(user_id=4, feature_request_id=4,
                          text="Hello Michael, what's happening? Just make"
                          "sure to get the cover sheets on the TPS reports.")

        # Set up, test the results.
        self.db.session.add(fr)
        self.db.session.add(comment)
        self.db.session.commit()

        saved_fr = FeatureRequest.query.filter_by(client_id=3, identifier=1).first()
        saved_comment = Comment.query.filter_by(user_id=4, feature_request_id=4).first()

        assert saved_fr.created
        assert saved_comment.created

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
