import os
import json
from datetime import datetime

import flask
import psycopg2

from main import get_hackathon_calendars

app = flask.Flask(__name__, static_url_path="")
conn = psycopg2.connect(os.environ.get("COCKROACH_DSN"))


@app.route("/")
def send_index():
    return flask.send_from_directory("../frontend", "index.html")


@app.route("/events")
def get_events():
    return get_events_cached_cockroachdb()


get_events_cached_timestamp = datetime.fromtimestamp(0)
get_events_cached_value = None


def get_events_cached_cockroachdb():
    global get_events_cached_timestamp
    global get_events_cached_value

    now = datetime.now()
    if (now - get_events_cached_timestamp).days > 1:
        get_events_cached_timestamp = now
        get_events_cached_value = get_hackathon_calendars_dict()

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Cache (entry) VALUES (%s)",
                (json.dumps(get_events_cached_value),),
            )
        conn.commit()

        return get_events_cached_value

    with conn.cursor() as cur:
        cur.execute("SELECT entry FROM Cache")
        entry = cur.fetchone()
        return json.loads(entry[0])


def get_hackathon_calendars_dict():
    hackathon_calendars = get_hackathon_calendars("https://mlh.io/seasons/2022/events/")
    for hackathon in hackathon_calendars:
        for event in hackathon_calendars[hackathon]:
            hackathon_calendars[hackathon][event] = str(
                hackathon_calendars[hackathon][event]
            )

    return hackathon_calendars


def setup_database():
    with conn.cursor() as cur:
        cur.execute("CREATE DATABASE IF NOT EXISTS HackCal")
        cur.execute("USE HackCal")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Cache (entry TEXT)
        """
        )
    conn.commit()


if __name__ == "__main__":
    setup_database()
    app.run()
