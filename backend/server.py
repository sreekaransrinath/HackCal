import flask

from main import get_hackathon_calendars

app = flask.Flask(__name__, static_url_path="")


@app.route("/")
def send_index():
    return flask.send_from_directory("../frontend", "index.html")


@app.route("/events")
def get_events():
    hackathon_calendars = get_hackathon_calendars("https://mlh.io/seasons/2022/events/")
    for hackathon in hackathon_calendars:
        for event in hackathon_calendars[hackathon]:
            hackathon_calendars[hackathon][event] = str(
                hackathon_calendars[hackathon][event]
            )

    return hackathon_calendars


if __name__ == "__main__":
    app.run()
