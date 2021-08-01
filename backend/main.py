# Scrape MLH Events Website and add individual events to cal via gcal API

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import pandas as pd
import time
from ics import Calendar, Event

"""
Steps:
    - Get list of events and urls from https://mlh.io/seasons/2022/events/ and store them in a list of tuples
    - For each event, 
        - Visit the webpage and scrape the table of events and deadlines.
        - Create a calendar using GCal API.
        - Dump all mini events and deadlines into the calendar.
        - Make calendar public.
        - If possible, generate ical file and upload to google calendar.
"""

# Step 1 - Get list of events and urls from https://mlh.io/seasons/2022/events/


def main():
    hackathon_calendars = get_hackathon_calendars("https://mlh.io/seasons/2022/events/")
    for hackathon in hackathon_calendars:
        for event in hackathon_calendars[hackathon]:
            hackathon_calendars[hackathon][event] = str(
                hackathon_calendars[hackathon][event]
            )

    print(hackathon_calendars)


def get_hackathon_calendars(url):
    hackathon_calendars = {}

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for hackathon_url in soup.select(".row:first-child .event-link"):
        if not hackathon_url["href"].startswith("https://organize.mlh.io"):
            continue

        response = requests.get(hackathon_url["href"], headers={"Accept": "text/html"})
        hackathon_soup = BeautifulSoup(response.text, "html.parser")
        dfs = pd.read_html(response.text)

        hackathon_name = hackathon_soup.select_one("h1").text
        hackathon_start_date = datetime.strptime(
            hackathon_soup.select_one("[itemprop = startDate]")["content"],
            "%Y-%m-%d %H:%M:%S %Z",
        )
        hackathon_end_date = datetime.strptime(
            hackathon_soup.select_one("[itemprop = endDate]")["content"],
            "%Y-%m-%d %H:%M:%S %Z",
        )

        calendar = {}

        for df in dfs:
            for i in range(df.shape[0]):
                event_day = df.loc[i].at["Day (ET)"].split()[0]
                event_time = " ".join(df.loc[i].at["ET"].split()[:-1])
                event_name = df.loc[i].at["Event"]
                event_dates = {
                    "Friday": hackathon_start_date,
                    "Saturday": hackathon_start_date + timedelta(days=1),
                    "Sunday": hackathon_start_date + timedelta(days=2),
                }
                event_date = event_dates[event_day].strftime("%Y-%m-%d")
                event_time = (
                    datetime.strptime(event_time, "%I:%M %p").time().strftime("%H:%M")
                )
                event_end_time = (
                    (datetime.strptime(event_time, "%H:%M") + timedelta(minutes=30))
                    .time()
                    .strftime("%H:%M")
                )

                event = Event()
                event.name = f"{hackathon_name} - {event_name}"
                event.begin = f"{event_date} {event_time}"
                event.end = f"{event_date} {event_end_time}"
                event.timezone = "America/New_York"

                calendar[event_name] = event

        hackathon_calendars[hackathon_name] = calendar

    return hackathon_calendars


if __name__ == "__main__":
    main()
