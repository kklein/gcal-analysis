import datetime
import os

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
APPLICATION_NAME = "Google Calendar API Python Quickstart"
CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = "https://www.googleapis.com/auth/calendar.readonly"

# Events with colorcoding 'Flamingo'. 'Flamingo' is encoded as 4.
RUNNING_SUMMARY = "Running"
SPORT_COLOR = "4"


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, "calendar-python-quickstart.json")
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print("Storing credentials to " + credential_path)
    return credentials


def summary_filter(event):
    return (
        "summary" in event
        and "description" in event
        and event["summary"] == RUNNING_SUMMARY
    )


def color_filter(event):
    return "colorId" in event and event["colorId"] == SPORT_COLOR


def get_events(timestamp_start, timestamp_end):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http)
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=timestamp_start,
            timeMax=timestamp_end,
            maxResults=100000,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])


def get_filtered_events(timestamp_start, timestamp_end, filter_kind):
    events = get_events(timestamp_start, timestamp_end)
    if filter_kind == "summary":
        return list(filter(summary_filter, events))
    elif filter_kind == "color":
        return list(filter(color_filter, events))
