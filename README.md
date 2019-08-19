# gcal-analysis

## Description

This script queries events from google calendar, filters them based on color coding and description, aggregates them on a weekly basis and plots the weekly aggregates.

My use cases are:
 - filtering the event descriptions for running indications and adding up distances run in a given week
 - filtering event colors for sport activity indications and counting how many there were in a given week

I followed [google's calendar quickstart in python](https://developers.google.com/google-apps/calendar/quickstart/python).

## Usage

Follow aforementioned guide and place a client_secret.json file in the cloned folder.

Run the script by executing `python analysis.py`. If running this script for the first time, you'll be prompted to sign in with OAUTH2 in your browser.

I hope the code is fairly self-explanatory. :)


## In development: Interactive d3 visualization.
Run:
`python -m http.server 8000`
Inspiration:
- https://www.d3-graph-gallery.com/graph/interactivity_zoom.html
- https://bl.ocks.org/mbostock/431a331294d2b5ddd33f947cf4c81319
- https://stackoverflow.com/questions/41196044/get-iso-week-day-and-week-of-year-in-d3
- http://learnjsdata.com/group_data.html
- https://www.d3-graph-gallery.com/graph/barplot_button_data_hard.html
- http://bl.ocks.org/d3noob/a22c42db65eb00d4e369
