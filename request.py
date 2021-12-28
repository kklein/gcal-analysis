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

RUNNING_SUMMARY = "running"
CYCLING_SUMMARY = "cycling"
GYM_SUMMARY = "gym"
# Events with colorcoding 'Flamingo'. 'Flamingo' is encoded as 4.
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


def get_summary_filter(summary):
    def summary_filter(event):
        # DIRT HACK
        if summary == GYM_SUMMARY:
            return (
                "summary" in event
                # Gym events can come as 'Gym', 'Gym:ub', 'Gym:lb', etc.
                and event["summary"].lower().startswith(summary)
            )
        return (
            "summary" in event
            and "description" in event
            # Running and Cycling events are excatly called that way.
            # Some social, non-desired events are called 'Running w/ friend'
            # and should not be considered.
            and event["summary"].lower() == summary
        )
    return summary_filter


def get_color_filter(color):
    def color_filter(event):
        return "colorId" in event and event["colorId"] == color
    return color_filter


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


def get_filtered_events(timestamp_start, timestamp_end, filter_kind, filter_value):
    events = get_events(timestamp_start, timestamp_end)
    if filter_kind == "summary":
        filter_function = get_summary_filter(summary=filter_value)
    elif filter_kind == "color":
        filter_function = get_color_filter(color=filter_value)
    return list(filter(filter_function, events))
