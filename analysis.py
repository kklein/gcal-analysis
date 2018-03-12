import datetime
import httplib2
import matplotlib
import matplotlib.patches as mpatches
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
START_DATE = datetime.datetime(2016, 9, 10)
# Events with colorcoding 'Flamingo', i.e. 4.
SPORT_COLOR = '4'
RUNNING_SUMMARY = 'Running'

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
    """Obtains all events between START_DATE and current time and filters them
    by indication of sports events. Provides simple plots.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # 'Z' indicates UTC time
    timeStart = START_DATE.isoformat() + 'Z'
    timeNow = datetime.datetime.utcnow().isoformat() + 'Z'

    eventsResult = service.events().list(
        calendarId='primary', timeMin=timeStart, timeMax = timeNow,
        maxResults=100000, singleEvents=True, orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    print('Total number of events before filterting: ' + str(len(events)))

    # Events with summary 'Running'.
    summaryFilteredEvents = []
    colorFilteredEvents = []
    for event in events:
        if 'summary' in event and event['summary'] == RUNNING_SUMMARY:
            summaryFilteredEvents.append(event)
        if 'colorId' in event and event['colorId'] == SPORT_COLOR:
            colorFilteredEvents.append(event)

    print('Total number of events with summary Running: ' +
        str(len(summaryFilteredEvents)))
    print('Total number of events with color Flamingo: ' +
        str(len(colorFilteredEvents)))

    # Plot1: Running distances.
    # Compute the running distance per week.
    distancePerWeek = defaultdict(lambda: 0)
    firstDate = matplotlib.dates.datestr2num(
        [summaryFilteredEvents[0]['start']['dateTime']])
    lastDate = matplotlib.dates.datestr2num(
        [summaryFilteredEvents[len(summaryFilteredEvents) - 1]['start']['dateTime']])
    for week_id in range(dateToWeek(firstDate, firstDate), dateToWeek(lastDate, firstDate)):
        distancePerWeek[week_id] = 0

    for event in summaryFilteredEvents:
        if 'description' in event:
            distancePerWeek[dateToWeek(
                matplotlib.dates.datestr2num([event['start']['dateTime']]),
                firstDate)] += descriptionToDistance(event['description'])

    aggregatedWeekDates, aggregatedDistances = zip(*distancePerWeek.items())
    averageDistance = sum(aggregatedDistances)/len(aggregatedDistances)
    print ('Average distance per week: ' + str(averageDistance))

    plt.axhline(y=averageDistance, color='r', linestyle='-', label='average distance')
    plt.legend()
    plt.scatter(aggregatedWeekDates, aggregatedDistances)
    plt.xlabel('week number since start date')
    plt.ylabel('cumulative weekly distance [km]')
    plt.title('Running distances since: ' + START_DATE.strftime('%Y %m %d'))
    plt.show()

    # Plot2: Sports activities.
    # Compute the number of sport events per week.
    sportPerWeek = defaultdict(lambda: 0)
    firstDate = matplotlib.dates.datestr2num(
        [colorFilteredEvents[0]['start']['dateTime']])
    lastDate = matplotlib.dates.datestr2num(
        [colorFilteredEvents[len(colorFilteredEvents) - 1]['start']['dateTime']])
    for week_id in range(dateToWeek(firstDate, firstDate), dateToWeek(lastDate, firstDate)):
        sportPerWeek[week_id] = 0
    for event in colorFilteredEvents:
        sportPerWeek[dateToWeek(
            matplotlib.dates.datestr2num([event['start']['dateTime']]),
            firstDate)] += 1

    aggregatedWeekDates, aggregatedSportCount = zip(*sportPerWeek.items())

    averageSportsCount = len(colorFilteredEvents) / len(aggregatedWeekDates)
    print ('Average number of sports events per week: ' +
        str(averageSportsCount))

    plt.axhline(y=averageSportsCount, color='r', linestyle='-',
        label='average #activities')
    plt.legend()
    plt.scatter(aggregatedWeekDates, aggregatedSportCount)
    plt.xlabel('week number since start date')
    plt.ylabel('#weekly sports activities')
    plt.title('Sport activities since: ' + START_DATE.strftime('%Y %m %d'))
    plt.show()

if __name__ == '__main__':
    main()
