import argparse
import unittest

from iws_fr import app
from iws_fr.config import TestingConfig, DevelopmentConfig


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', action='store')

    args = parser.parse_args()

    # TODO: Add fixtures for regular data.
    # TODO: Command to load/dump fixtures.
    if args.command == 'test':
        app.config.from_object(TestingConfig)

        from iws_fr import tests
        test_suite = unittest.TestLoader().loadTestsFromModule(tests)
        unittest.TextTestRunner().run(test_suite)

    else:
        app.config.from_object(DevelopmentConfig)

        if args.command == 'setup':
            from iws_fr.models import db
            db.create_all()

        elif args.command == 'runserver':
            import iws_fr.views
            app.run()
