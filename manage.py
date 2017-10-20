import argparse
import unittest

from iws_fr import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', action='store')

    args = parser.parse_args()

    if args.command == 'test':
        app.config.from_object('config.TestingConfig')

        from iws_fr import tests
        test_suite = unittest.TestLoader().loadTestsFromModule(tests)
        unittest.TextTestRunner().run(test_suite)

    # TODO: Possibly clean up by having setup w/ arg for which environment.
    elif args.command == 'setup-dev':
        app.config.from_object('config.DevelopmentConfig')
        from iws_fr.models import db
        db.create_all()

    elif args.command == 'setup-prod':
        app.config.from_object('config.ProductionConfig')
        from iws_fr.models import db
        db.create_all()

    elif args.command == 'runserver':
        app.config.from_object('config.DevelopmentConfig')
        import iws_fr.views
        app.run()
