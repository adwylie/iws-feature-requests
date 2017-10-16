import argparse
import unittest

from iws_fr import tests
from iws_fr.settings import app
from iws_fr.settings import db


# TODO: Better argparser creation wrt/ help and documentation.
parser = argparse.ArgumentParser(
    description='Simple feature requests using Flask/SqlAlchemy/Knockout.',
    usage="""
    Type 'manage.py <subcommand> to run a specific command.

    Available subcommands:

    setup           Creates the database.
    test            Run unit tests.
    runserver       Runs a development server.
    """
)

parser.add_argument('command', action='store')

args = parser.parse_args()

if args.command == 'setup':
    db.create_all()

elif args.command == 'test':
    test_suite = unittest.TestLoader().loadTestsFromModule(tests)
    unittest.TextTestRunner().run(test_suite)

elif args.command == 'runserver':
    app.run(host='0.0.0.0')
