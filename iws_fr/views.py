from iws_fr import app


# TODO: Templates.
# TODO: Model forms?
@app.route('/')
def main():
    return "Hello World!"
