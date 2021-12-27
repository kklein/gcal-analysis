# gcal-analysis

This repo is meant to query google calendar events and produce some simple graphs/visualizations thereof.

My use cases are:
 - Filtering the event titles for running indications and retrieving distance information from the event descriptions. Also, accumulate distances per week.
 - Filtering event colors for sport activity indications and counting the occurrences.

Said use cases are explored in a jupyter notebook, `investigation.ipynb`. 

I once produced some interactive d3 visualization in `index.html` revolving around the same topic - this application is currently not tested.

## Python notebook

Follow [google's calendar quickstart in python](https://developers.google.com/google-apps/calendar/quickstart/python).
and place a `client_secret.json` in the root of this repository.
 
After having created the environment specified in `environment.yml`, authenticate by running `authenticate.py`. When running this script for the first time, you'll be prompted to sign in with OAUTH2 in your browser. Once you've done this, it should no longer be necessary to repeat this step on your system.

Run `jupyter notebook` and open `investigation.ipynb`.

## d3 visualization [currently not tested]

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
