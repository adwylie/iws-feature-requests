import argparse
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

elif args.command == 'run':
    # TODO: Fix this.
    subprocess.run('flask run')
