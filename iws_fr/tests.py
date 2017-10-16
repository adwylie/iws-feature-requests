import os
import unittest
import tempfile
from flask_fixtures import FixturesMixin

from .settings import app
from .settings import db
from .models import Client


# TODO: Write more tests!
# TODO: Fixtures:
#  Default users, some product areas,
# TODO: Test:
#  DB-level FR positive priority constraint,
#  DB-level FR unique priority constraint,
#  App-level FR priority inserts,
#  App-level FR target_date >= today,
#  App-level FR identifier auto-set on save (wrt/ client),
#  DB-level Comment default created datetime,
#  Restful api available methods??,
#  User full_name property read, set not allowed,

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
