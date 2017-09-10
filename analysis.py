from __future__ import print_function
import httplib2
import matplotlib
import matplotlib.pyplot as plt
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


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

def descriptionToDistance(description):
    return float(description.split('km')[0])

def processDate(date, firstDate):
    diff = int(date) - firstDate
    result = diff // 7
    return result

def main():
    """TODO(kkleindev)
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    timeStart = datetime.datetime(2016, 9, 10).isoformat() + 'Z'
    timeNow = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=timeStart, timeMax = timeNow, maxResults=100000, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    # meta stats
    print('Total number of events before filterting: ' + str(len(events)))

    descriptionFilteredEvents = []
    colorFilteredEvents = []
    intersection = []
    for event in events:
        #if 'colorId' in event and event['colorId'] == '4':
        if 'summary' in event and event['summary'] == 'Running':
            descriptionFilteredEvents.append(event)
        if 'colorId' in event and event['colorId'] == '4':
            colorFilteredEvents.append(event)
        if 'summary' in event and event['summary'] == 'Running' and 'colorId' in event and event['colorId'] == '4':
            intersection.append(event)
    print('Total number of events with description Running: ' + str(len(descriptionFilteredEvents)))
    print('Total number of events with color Flamingo: ' + str(len(colorFilteredEvents)))

#    intersection = descriptionEventSet.intersection(colorEventSet)

    print('Description && Color / Description: ' + str(len(intersection)/len(descriptionFilteredEvents)))
    print('Description && Color / Color: ' + str(len(intersection)/len(colorFilteredEvents)))

    dates = []
    distances = []

    for event in descriptionFilteredEvents:
        if 'description' in event:
            dates.append(event['start']['dateTime'])
            distances.append(descriptionToDistance(event['description']))

    dates = matplotlib.dates.datestr2num(dates)
    weekDates = []
    firstDate = ''
    for date in dates:
        if firstDate == '':
           firstDate = date
        weekDates.append(processDate(date, firstDate))

    pointer = 0

    aggregatedWeekDates = []
    aggregatedDistances = []

    currentDistance = 0
    currentWeek = weekDates[0]

    while pointer < len(distances):
        if weekDates[pointer] == currentWeek:
            currentDistance += distances[pointer]
        else:
            aggregatedWeekDates.append(currentWeek)
            aggregatedDistances.append(currentDistance)
            currentWeek = weekDates[pointer]
            currentDistance = distances[pointer]
        pointer += 1

    aggregatedWeekDates.append(currentWeek)
    aggregatedDistances.append(currentDistance)

    averageDistance = sum(aggregatedDistances)/len(aggregatedDistances)

    plt.axhline(y=averageDistance, color='r', linestyle='-')
    plt.scatter(aggregatedWeekDates,aggregatedDistances)
    plt.show()


if __name__ == '__main__':
    main()
