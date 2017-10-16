import os
import unittest
import tempfile
from flask_fixtures import FixturesMixin

from .settings import app
from .settings import db
from .models import Client


# TODO: Write more tests!
class FlaskTestCase(unittest.TestCase, FixturesMixin):
    fixtures = ['clients.json']
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
    def test_default_clients(self):
        clients = Client.query.all()
        assert len(clients) == Client.query.count() == 3


if '__main__' == __name__:
    unittest.main()
