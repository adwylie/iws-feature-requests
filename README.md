## IWS Feature Requests

Toy project using Flask/SqlAlchemy/Knockout to implement feature requests. Written as part of the application process for a mid-level software engineering position, and also kind of for fun..

Unfortunately it's quite rare I complete a personal project from start to finish, so we'll see how this ends up. Some background info for those that find this interesting and want to have a similar setup:
* [Free Continuous Deployment (Simon Willison)](https://simonwillison.net/2017/Oct/17/free-continuous-deployment/)

### Running Development Locally

1. Clone the repository: `git clone git@github.com:adwylie/iws-feature-requests.git`.
2. Create a virtual environment (python 3.6) in the project directory and activate it:
    ```
    cd iws-feature-requests
    virtualenv --python=python3 env
    source env/bin/activate
    ```
3. Install required libraries: `pip install -r requirements.txt`.
4. Set up environment variables:
   ```
    export SECRET_KEY='verysecret'
    export RECAPTCHA_PUBLIC_KEY='<public key>'
    export RECAPTCHA_PRIVATE_KEY='<private key>'
   ```
5. Set up the sqlite database: `python manage.py setup`.
6. Load data fixtures (optional): `python manage.py loaddata`.
7. Run the development server: `python manage.py runserver`.
8. Lastly, navigate to `http://127.0.0.1:5000/` in the web browser of your choice.

Tests can also be run using the command `python manage.py test`.
