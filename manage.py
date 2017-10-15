import argparse
import os
import subprocess

parser = argparse.ArgumentParser(
    description='Simple feature requests using Flask/SqlAlchemy/Knockout.'
)

# help='Execute initial program setup.',
# help='Run the program.',
parser.add_argument('command', action='store')

args = parser.parse_args()

if args.command == 'setup':
    from iws_fr.models import db
    db.create_all()

elif args.command == 'runserver':
    environment = dict(os.environ.copy())
    environment['FLASK_APP'] = 'iws_fr/views.py'

    try:
        subprocess.run(
            ['python', '-m', 'flask', 'run', '--host=0.0.0.0'],
            env=environment,
        )
    except KeyboardInterrupt:
        pass
