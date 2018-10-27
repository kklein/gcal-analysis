import datetime
import os
from collections import defaultdict

import httplib2
import matplotlib.pyplot as plt
import strict_rfc3339

from apiclient import discovery

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#TODO(kkleindev): What's argparse?
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
START_DATE = datetime.datetime(2016, 9, 10)
# Events with colorcoding 'Flamingo'. 'Flamingo' is encoded as 4.
RUNNING_SUMMARY = 'Running'
SPORT_COLOR = '4'

# Taken from https://mail.python.org/pipermail/tutor/2013-July/096752.html
def ywd_to_date(year, week, weekday):
    """Convert (year, week, isoweekday) tuple to a datetime.date().

    >>> datetime.date(2013, 7, 12).isocalendar()
    (2013, 28, 5)
    >>> ywd_to_date(2013, 28, 5)
    datetime.date(2013, 7, 12)
    """
    first = datetime.date(year, 1, 1)
    first_year, _first_week, first_weekday = first.isocalendar()

    if first_year == year:
        week -= 1

    return first + datetime.timedelta(days=week*7+weekday-first_weekday)

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_events(timestamp_start, timestamp_end):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    events_result = service.events().list(
        calendarId='primary', timeMin=timestamp_start, timeMax=timestamp_end,
        maxResults=100000, singleEvents=True, orderBy='startTime').execute()
    return events_result.get('items', [])

def summary_filter(event):
    return ('summary' in event and
            'description' in event and
            event['summary'] == RUNNING_SUMMARY)

def color_filter(event):
    return 'colorId' in event and event['colorId'] == SPORT_COLOR

def date_str_to_date(date_str):
    timestamp = strict_rfc3339.rfc3339_to_timestamp(date_str)
    return datetime.date.fromtimestamp(timestamp)

def date_to_first_day_of_week(date):
    year, week = date.isocalendar()[0:2]
    day = 0
    return ywd_to_date(year, week, day)

def compute_distance_metric(event):
    return float(event['description'].split('km')[0])

def compute_count_metric(event):
    return 1

# TODO(kkleindev): Consider filling up weeks with 0 events as to paint a more
# 'complete' picture.
# Metric has to cummulative via addition.
def get_accumulated_date_evaluations(events, compute_metric):
    date_strings = list(map(lambda x: x['start']['dateTime'], events))
    dates = list(map(date_str_to_date, date_strings))
    weekly_dates = list(map(date_to_first_day_of_week, dates))
    evaluations = list(map(compute_metric, events))
    dict = defaultdict(int)
    for (weekly_date, evaluation) in zip(weekly_dates, evaluations):
        dict[weekly_date] += evaluation
    return list(dict.keys()), list(dict.values())

def plot_weekly_evaluations(week_dates, aggregated_evaluations,
                            unit_description, unit=None):
    if unit is None:
        unit_string = ''
    else:
        unit_string = '[%s]' % unit

    average_evaluation = sum(aggregated_evaluations) / len(aggregated_evaluations)
    plt.plot_date(x=week_dates, y=aggregated_evaluations, xdate=True,
                  ydate=False)
    plt.axhline(y=average_evaluation, color='r', linestyle='-',
                label='Average %s %.2f %s' %
                (unit_description, average_evaluation, unit_string))
    plt.ylabel('Cumulative weekly %ss %s' % (unit_description, unit_string))
    plt.title('Weekly %s since: %s' %
              (unit_description, START_DATE.strftime('%Y %m %d')))
    plt.legend()
    plt.show()

def main():
    """Obtain all events between START_DATE and current time. Filters them
    by indication of sport events. Provide simple plots.
    """
    # 'Z' indicates UTC time
    timestamp_start = START_DATE.isoformat() + 'Z'
    timestamp_now = datetime.datetime.utcnow().isoformat() + 'Z'
    events = get_events(timestamp_start, timestamp_now)
    print('Total number of events before filterting: ' + str(len(events)))

    # Running part.
    summary_filtered_events = list(filter(summary_filter, events))
    print('Total number of events with summary Running: %d' %
          len(summary_filtered_events))
    dates, distances = get_accumulated_date_evaluations(
        summary_filtered_events, compute_distance_metric)
    plot_weekly_evaluations(dates, distances, 'running distance', 'km')

    # Sport activities part.
    color_filtered_events = list(filter(color_filter, events))
    print('Total number of events with color Flamingo: %d' %
          len(color_filtered_events))
    dates, counts = get_accumulated_date_evaluations(
        color_filtered_events, compute_count_metric)
    plot_weekly_evaluations(dates, counts, 'activity count')

if __name__ == '__main__':
    main()
