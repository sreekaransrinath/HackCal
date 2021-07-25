import flask
import base64

from main import get_hackathon_calendars

app = flask.Flask(__name__)


@app.route("/events")
def get_events():
    hackathon_calendars = get_hackathon_calendars("https://mlh.io/seasons/2022/events/")
    for hackathon in hackathon_calendars:
        hackathon_calendars[hackathon] = base64.b64encode(
            str(hackathon_calendars[hackathon]).encode()
        ).decode()

    return hackathon_calendars


if __name__ == "__main__":
    app.run()
