#Scrape MLH Events Website and add individual events to cal via gcal API

import requests
from bs4 import BeautifulSoup
import datetime
import re
import pandas as pd
import webbrowser
import time

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}
'''
Steps:
    - Get list of events and urls from https://mlh.io/seasons/2022/events/ and store them in a list of tuples
    - For each event, 
        - Visit the webpage and scrape the table of events and deadlines.
        - Create a calendar using GCal API.
        - Dump all mini events and deadlines into the calendar.
        - Make calendar public.
        - If possible, generate ical file and upload to google calendar.
'''

#Step 1 - Get list of events and urls from https://mlh.io/seasons/2022/events/

response = requests.get('https://mlh.io/seasons/2022/events/')
soup = BeautifulSoup(response.text, 'html.parser')

event_names = [event.text for event in soup.find_all('h3', class_='event-name')]
event_dates = soup.find_all('p', class_='event-date')
event_urls = [url['href'] for url in soup.find_all('a', class_='event-link')]

hackathon_dates = []
#Figure out whether each of the dates is after this, and discard the events that have dates before today.
today = datetime.date.today()
event_count = 0
for event_date in event_dates:
    date = re.findall(r"^[\w]{3} [\d]+", event_date.text)
    date[0] += (" 2021")
    hackdate = datetime.datetime.strptime(date[0], '%b %d %Y').date()
    if hackdate > today:
        hackathon_dates.append(hackdate)
        event_count += 1

events = list(zip(event_names[:event_count], event_urls[:event_count]))
events = [event for event in events if event[1].startswith('https://organize.mlh.io')]

for i in range(len(events)):
    url = events[i][1]
    print(url)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    dfs = pd.read_html(response.text)

    for df in dfs:
        for i in range(df.shape[0]):
            event_day = df.loc[i].at["Day (ET)"].split()[0]
            event_time = " ".join(df.loc[i].at["ET"].split()[:-1])
            event_name = df.loc[i].at["Event"]
            event_dates = {
                'Friday': hackathon_dates[i],
                'Saturday': hackathon_dates[i] + datetime.timedelta(days=1),
                'Sunday': hackathon_dates[i] + datetime.timedelta(days=2)
            }
            event_date = event_dates[event_day].strftime("%Y-%m-%d")
            event_time = datetime.datetime.strptime(event_time, '%I:%M %p').time().strftime('%H:%M')
            event_end_time = (datetime.datetime.strptime(event_time, '%H:%M') + datetime.timedelta(minutes=30)).time().strftime('%H:%M')
            print(event_date, event_time, event_end_time, event_name)
            webbrowser.open(f"https://calndr.link/d/event/?service=google&start={event_date} {event_time}&end={event_date} {event_end_time}&title={event_name}&timezone=America/New_York")
            time.sleep(20)