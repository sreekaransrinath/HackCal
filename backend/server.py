import flask
import base64
from ics import Calendar

from main import get_hackathon_calendars

app = flask.Flask(__name__, static_url_path='')

@app.route('/')
def send_index():
    return flask.send_from_directory("../frontend", "index.html")

@app.route("/events")
def get_events():
    hackathon_calendars = get_hackathon_calendars("https://mlh.io/seasons/2022/events/")
    
    all_hackathon_calendars = Calendar()
    for hackathon in hackathon_calendars:
        all_hackathon_calendars.events.update(hackathon_calendars[hackathon].events)
    hackathon_calendars["ALL_CALENDARS"] = all_hackathon_calendars
    
    for hackathon in hackathon_calendars:
        hackathon_calendars[hackathon] = base64.b64encode(
            str(hackathon_calendars[hackathon]).encode()
        ).decode()

    return hackathon_calendars


if __name__ == "__main__":
    app.run()
