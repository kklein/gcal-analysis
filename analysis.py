import datetime
import httplib2
import matplotlib
import matplotlib.pyplot as plt
import os

from apiclient import discovery
from collections import defaultdict
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

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
START_TIME = datetime.datetime(2016, 9, 10).isoformat()

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

def dateToWeek(date, firstDate):
    """Returns the week number of the date from firstDate.
    """
    return (int(date) - int(firstDate)) // 7

def main():
    """TODO(kkleindev)
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # 'Z' indicates UTC time
    timeStart = START_TIME + 'Z'
    timeNow = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=timeStart, timeMax = timeNow,
        maxResults=100000, singleEvents=True, orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    print('Total number of events before filterting: ' + str(len(events)))

    descriptionFilteredEvents = []
    colorFilteredEvents = []
    intersection = []
    for event in events:
        if 'summary' in event and event['summary'] == 'Running':
            descriptionFilteredEvents.append(event)
        if 'colorId' in event and event['colorId'] == '4':
            colorFilteredEvents.append(event)

    print('Total number of events with description Running: ' +
        str(len(descriptionFilteredEvents)))
    print('Total number of events with color Flamingo: ' +
        str(len(colorFilteredEvents)))

    # Compute the running distance per week.
    sportPerWeek = defaultdict(lambda: 0)
    firstDate = matplotlib.dates.datestr2num(
        [descriptionFilteredEvents[0]['start']['dateTime']])
    for event in descriptionFilteredEvents:
        if 'description' in event:
            sportPerWeek[dateToWeek(
                matplotlib.dates.datestr2num([event['start']['dateTime']]),
                firstDate)] += descriptionToDistance(event['description'])

    aggregatedWeekDates, aggregatedDistances = zip(*sportPerWeek.items())

    averageDistance = sum(aggregatedDistances)/len(aggregatedDistances)
    print ('Average distance per week: ' + str(averageDistance))

    plt.axhline(y=averageDistance, color='r', linestyle='-')
    plt.scatter(aggregatedWeekDates, aggregatedDistances)
    plt.show()

    # Compute the number of sport events per week.
    sportPerWeek = defaultdict(lambda: 0)
    firstDate = matplotlib.dates.datestr2num(
        [colorFilteredEvents[0]['start']['dateTime']])
    for event in colorFilteredEvents:
        sportPerWeek[dateToWeek(
            matplotlib.dates.datestr2num([event['start']['dateTime']]),
            firstDate)] += 1

    aggregatedWeekDates, aggregatedSportCount = zip(*sportPerWeek.items())

    averageSportsCount = len(colorFilteredEvents) / len(aggregatedWeekDates)
    print ('Average number of sports events per week: ' +
        str(averageSportsCount))

    plt.axhline(y=averageSportsCount, color='r', linestyle='-')
    plt.scatter(aggregatedWeekDates, aggregatedSportCount)
    plt.show()

if __name__ == '__main__':
    main()
