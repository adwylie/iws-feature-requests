import argparse
import os
import sys
import unittest

from iws_fr import app
from iws_fr.config import TestingConfig, DevelopmentConfig


def date_deserialize(obj):
    """JSON deserializer for objects not serializable by default."""
    from dateutil.parser import parse

    # Names of any unserializable model fields.
    keys = ['target_date', 'created']

    for key in keys:
        value = obj.get(key)
        if value:
            obj[key] = parse(value)

    return obj


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', action='store')

    args = parser.parse_args()

    # TODO: Update fixtures.
    # TODO: Command to dump fixtures?
    if args.command == 'test':
        app.config.from_object(TestingConfig)

        from iws_fr import tests
        test_suite = unittest.TestLoader().loadTestsFromModule(tests)
        result = unittest.TextTestRunner().run(test_suite)
        sys.exit(not result.wasSuccessful())

    else:
        app.config.from_object(DevelopmentConfig)

        if args.command == 'setup':
            from iws_fr.models import db
            db.create_all()

        elif args.command == 'loaddata':
            # Note: The load_fixtures function isn't in flask_fixtures public API.
            # TODO: Order isn't be correct for loading. IMPORTANT
            from iws_fr.models import db
            import json
            from flask_fixtures import load_fixtures

            fixtures_directory = os.path.join('iws_fr', 'fixtures')
            fixtures = os.listdir(fixtures_directory)
            for fixture in fixtures:
                fixture_directory = os.path.join(fixtures_directory, fixture)
                with open(fixture_directory) as fixture_file:
                    fixture_data = json.loads(
                        fixture_file.read(), object_hook=date_deserialize)
                    load_fixtures(db, fixture_data)

        elif args.command == 'runserver':
            # TODO: Update to flask run cmdline.
            # TODO: libsass to compile css?
            # https://stackoverflow.com/questions/9508667/reload-flask-app-when-template-file-changes
            # https://hongminhee.org/libsass-python/
            # http://flask.pocoo.org/docs/0.12/server/
            # https://github.com/arnaudlimbourg/heroku-libsass-python
            # https://codepen.io/adwylie/
            # https://github.com/postcss/autoprefixer
            # cssnano
            import iws_fr.views
            app.run()
