
# if command == setup, import etc.
from .models import db
db.create_all()


# run
# FLASK_APP＝..views.py
# flask run

