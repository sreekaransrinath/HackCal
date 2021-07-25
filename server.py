import flask

app = flask.Flask(__name__)

@app.route('/events')
def hello_world():
    return {
        "message": "Hello World"
    }
