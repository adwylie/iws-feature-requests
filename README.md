## IWS Feature Requests [![Build Status](https://travis-ci.org/adwylie/iws-feature-requests.svg?branch=master)](https://travis-ci.org/adwylie/iws-feature-requests) [![Deploy Status](https://heroku-badge.herokuapp.com/?app=adwylie-iws-feature-requests&style=flat&svg=1)](https://adwylie-iws-feature-requests.herokuapp.com/)

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
4. Set up the database (sqlite): `python manage.py setup`.
5. Run the development server: `python manage.py runserver`.

Tests can also be run using the command `python manage.py test`.

### Running Production Locally via Heroku

The project is set up to be automatically deployed to Heroku after unit tests pass (on travis). Perhaps for troubleshooting you (well, me actually) can run the project locally using the production database (postgresql).

1. After the first three steps above we need to log into heroku and set an environment variable.
    ```
    heroku auth:login
    DATABASE_URL=`heroku config:get DATABASE_URL -a adwylie-iws-feature-requests`
    ```
2. Then we can continue on to run the server using production db: `heroku local web`.
