# gcal-analysis

This repo is meant to query google calendar events and produce some simple graphs/visualizations thereof.

My use cases are:
 - Filtering the event titles for running indications and retrieving distance information from the event descriptions. Also, accumulate distances per week.
 - Filtering event colors for sport activity indications and counting the occurrences.

Said use cases are explored by producing graphs via a python script, `analysis.py`, as well as producing an interactive d3 visualization in `index.html`.

## Python script

I followed [google's calendar quickstart in python](https://developers.google.com/google-apps/calendar/quickstart/python).

Follow aforementioned guide and place a `client_secret.json` file in the root directory.

Run the script by executing `python analysis.py`. When running this script for the first time, you'll be prompted to sign in with OAUTH2 in your browser.

I hope the code is fairly self-explanatory. :)

## d3 visualization

### Features
- Tooltip when hovering over individual datapoint.
- X-axis is zoomable by scrolling anywhere over the visualization.
- X-axis is pannable once zoomed in.

### Usage

I followed [google's calendar browser quickstart](https://developers.google.com/calendar/quickstart/js).

Follow aforementioned guide and place a `secret.js` file in the root directory.
The file should contain two variable definitions:
``const CLIENT_ID = 'fill in your personal id obtained through the guide';
const API_KEY = 'fill in your personal api key obtained through the guide';``

Run `python -m http.server 8000` from the root directory and open the suggested url.

When running this script for the first time, you'll be prompted to sign in with OAUTH2 in your browser.

I intended to follows [Google's javascript style guide](https://google.github.io/styleguide/jsguide.html#naming).

I hope the code is fairly self-explanatory. :)

## Kudos/inspiration

- https://www.d3-graph-gallery.com/graph/interactivity_zoom.html
- https://bl.ocks.org/mbostock/431a331294d2b5ddd33f947cf4c81319
