// Array of API discovery doc URLs for APIs used by the quickstart
const DISCOVERY_DOCS = ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'];

// Authorization scopes required by the API; multiple scopes can be
// included, separated by spaces.
const SCOPES = 'https://www.googleapis.com/auth/calendar.readonly';

const authorizeButton = document.getElementById('authorize_button');
const signoutButton = document.getElementById('signout_button');

let state = true;

/**
 *  On load, called to load the auth2 library and API client library.
 */
function handleClientLoad() {
  gapi.load('client:auth2', initClient);
}

/**
 * Append a pre element to the body containing the given message
 * as its text node. Used to display the results of the API call.
 *
 * @param {string} message Text to be placed in pre element.
 */
function appendPre(message) {
  const pre = document.getElementById('content');
  const textContent = document.createTextNode(message + '\n');
  pre.appendChild(textContent);
}

/**
 *  Initializes the API client library and sets up sign-in state
 *  listeners.
 */
function initClient() {
  gapi.client.init({
    apiKey: API_KEY,
    clientId: CLIENT_ID,
    discoveryDocs: DISCOVERY_DOCS,
    scope: SCOPES,
  }).then(() => {
    // Listen for sign-in state changes.
    gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);

    // Handle the initial sign-in state.
    updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
    authorizeButton.onclick = handleAuthClick;
    signoutButton.onclick = handleSignoutClick;
  }, (error) =>
    appendPre(JSON.stringify(error, null, 2))
  );
}

/**
 *  Called when the signed in status changes, to update the UI
 *  appropriately. After a sign-in, the API is called.
 */
function updateSigninStatus(isSignedIn) {
  if (isSignedIn) {
    authorizeButton.style.display = 'none';
    signoutButton.style.display = 'block';
    displayEvents(state);
  } else {
    authorizeButton.style.display = 'block';
    signoutButton.style.display = 'none';
  }
}

/**
 *  Sign in the user upon button click.
 */
function handleAuthClick(event) {
  gapi.auth2.getAuthInstance().signIn();
}

/**
 *  Sign out the user upon button click.
 */
function handleSignoutClick(event) {
  gapi.auth2.getAuthInstance().signOut();
}

/**
 *  Given an event object, return a date object indicating its start.
 */
function extractDate(event) {
  if (event.start.dateTime) {
    return new Date(event.start.dateTime);
  }
  return new Date(event.start.date);
}


aggregateButton = document.getElementById('aggregate_button');
aggregateButton.onclick = () => {
  state = !state;
  // First get rid off previous visalization.
  const svg = document.querySelector('svg');
  const children = Array.from(svg.childNodes);
  children.forEach((child) =>
    child.parentNode.removeChild(child)
  );

  displayEvents(state);
};

function createWeeklyAggregates(data) {
  return d3.nest()
      .key((d) => d3.timeWeek(d.x))
      .rollup((group) => d3.sum(group, (d) => d.y))
      .entries(data)
      .map((d) => {
        return {
          x: new Date(d.key),
          y: d.value,
        };
      });
}

const tooltip = d3.select('body').append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0);

/**
 * Print the summary and start datetime/date of the next ten events in
 * the authorized user's calendar. If no events are found an
 * appropriate message is printed.
 */
function displayEvents(useAggregate) {
  gapi.client.calendar.events.list({
    'calendarId': 'primary',
    'timeMin': (new Date(2016, 9, 10)).toISOString(),
    'timeMax': (new Date()).toISOString(),
    'showDeleted': false,
    'singleEvents': true,
    'maxResults': 10000,
    'orderBy': 'startTime',
  }).then((response) => {
    // Filter and process calendar events.
    let events = response.result.items;
    if (events.length > 0) {
      events = events.filter((event) => event.summary == 'Running');
      events = events.filter(
          (event) => typeof event.description !== 'undefined');
      events.forEach((event) => {
        event.date = extractDate(event);
        event.distance = event.description.split(' ')[0];
      });

      let data = d3.range(events.length).map((i) => {
        return {
          x: events[i].date,
          y: +events[i].distance};
      });

      if (useAggregate) {
        data = createWeeklyAggregates(data);
      }

      const svg = d3.select('svg');
      const margin = {top: 20, right: 20, bottom: 30, left: 40};
      const width = +svg.attr('width') - margin.left - margin.right;
      const height = +svg.attr('height') - margin.top - margin.bottom;

      const translation = 'translate(' + margin.left + ',' + margin.top
          + ')';

      const xScaler = d3.scaleTime()
          .domain([new Date(2016, 9, 10), new Date()])
          .range([0, width]);

      const yScaler = d3.scaleLinear()
          .domain(d3.extent(data, (d) => d.y))
          .range([height, 0]);

      const xAxis = d3.axisBottom(xScaler);
      const yAxis = d3.axisLeft(yScaler);

      const initiateZoom = d3.zoom()
          .scaleExtent([1, 32])
          .translateExtent([[0, 0], [width, height]])
          .extent([[0, 0], [width, height]])
          .on('zoom', reactToZoom);

      // Define the area of the svg that can be 'used' and will not be
      // clipped.
      svg.append('defs').append('clipPath')
          .attr('transform', translation)
          .attr('id', 'clip')
          .append('rect')
          .attr('width', width)
          .attr('height', height);

      // Define child of svg that will actually contain elements.
      const g = svg.append('g')
          .attr('transform', translation);

      g.append('g')
          .attr('class', 'axis axis--x')
          .attr('transform', 'translate(0,' + height + ')')
          .call(xAxis);

      g.append('g')
          .attr('class', 'axis axis--y')
          .call(yAxis);

      g.append('g')
          .attr('clip-path', 'url(#clip)')
          .selectAll('.circle')
          .data(data)
          .enter().append('circle')
          .attr('class', 'datapoint')
          .attr('cx', (d) => xScaler(d.x))
          .attr('cy', (d) => yScaler(d.y))
          .attr('r', 3.5)
          .on('mouseover', (d) => {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(d.y.toFixed(2))
                .style('left', (d3.event.pageX) + 'px')
                .style('top', (d3.event.pageY - 28) + 'px');
          })
          .on('mouseout', (d) => {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
          });

      // Bind zooming to svg.
      svg.call(initiateZoom).transition();

      function reactToZoom() {
        const t = d3.event.transform;
        const xt = t.rescaleX(xScaler);
        g.select('.axis--x').call(xAxis.scale(xt));
        g.selectAll('circle')
            .attr('cx', (d) => xt(d.x));
      }
    }
  });
}
