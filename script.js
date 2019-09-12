// Array of API discovery doc URLs for APIs used by the quickstart
const DISCOVERY_DOCS = ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'];

// Authorization scopes required by the API; multiple scopes can be
// included, separated by spaces.
const SCOPES = 'https://www.googleapis.com/auth/calendar.readonly';

const authorizeButton = document.getElementById('authorize_button');

const startDate = new Date(2016, 9, 10);

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
    initializeVisualizion();
  } else {
    authorizeButton.style.display = 'block';
  }
}

/**
 *  Sign in the user upon button click.
 */
function handleAuthClick(event) {
  gapi.auth2.getAuthInstance().signIn();
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

function fillUpWeeks(data) {
  const firstDate = data[0].x;
  const lastDate = data[data.length-1].x;
  const allDates = d3.timeWeek.range(firstDate, lastDate);

  // The conversion to strings is necessary as Object equality won't work with
  // 'includes'.
  const presentDates = data.map((d) => d.x.toString());
  const newDates = allDates.filter((d) => !presentDates.includes(d.toString()));

  newDates.forEach((d) => data.push({x: d, y: 0}));
  return data;
}

function selectDataSet(checked, dailyData, weeklyData) {
  return checked ? weeklyData : dailyData;
}

function getReactToZoom(circleContainer, xScaler, xAxis) {
  return () => {
    const t = d3.event.transform;
    const xt = t.rescaleX(xScaler);
    circleContainer.select('.axis--x').call(xAxis.scale(xt));
    circleContainer.selectAll('circle')
        .attr('cx', (d) => xt(d.x));
  };
}

function initiateZoom(width, height, circleContainer, xScaler, xAxis) {
  return d3.zoom()
      .scaleExtent([1, 32])
      .translateExtent([[0, 0], [width, height]])
      .extent([[0, 0], [width, height]])
      .on('zoom', getReactToZoom(circleContainer, xScaler, xAxis));
}

function displayData(data) {
  const tooltip = d3.select('#tooltip');

  const svg = d3.select('svg');
  const margin = {top: 20, right: 20, bottom: 30, left: 60};
  const width = +svg.attr('width') - margin.left - margin.right;
  const height = +svg.attr('height') - margin.top - margin.bottom;

  console.log(height);

  const translation = 'translate(' + margin.left + ',' + margin.top
      + ')';

  const xScaler = d3.scaleTime()
      .domain(d3.extent(data, (d) => d.x))
      .range([0, width]);

  const yScaler = d3.scaleLinear()
      .domain(d3.extent(data, (d) => d.y))
      .range([height, 0]);

  const xAxis = d3.axisBottom(xScaler);
  const yAxis = d3.axisLeft(yScaler);

  // Define the area of the svg that can be 'used' and will not be
  // clipped.
  svg.append('defs')
      .append('clipPath')
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
      .selectAll('.circle')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'datapoint')
      .attr('cx', (d) => xScaler(d.x))
      .attr('cy', (d) => yScaler(d.y))
      .attr('r', 3.5)
      .on('mouseover', (d) => {
        tooltip.transition()
            .duration(200)
            .style('opacity', .9);
        tooltip.html(d.y.toFixed(2) + 'km')
            .style('left', (d3.event.pageX) + 'px')
            .style('top', (d3.event.pageY - 28) + 'px');
      })
      .on('mouseout', (d) => {
        tooltip.transition()
            .duration(500)
            .style('opacity', 0);
      });

  // Bind zooming to svg.
  svg.call(initiateZoom(width, height, g, xScaler, xAxis)).transition();

  // Add label to x-axis.
  svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 20)
      .attr('x', 0 - (height / 2))
      .style('text-anchor', 'middle')
      .text('distance [km]');
}

function initializeVisualizion() {
  gapi.client.calendar.events.list({
    'calendarId': 'primary',
    'timeMin': startDate.toISOString(),
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

      const dailyData = d3.range(events.length).map((i) => {
        return {
          x: events[i].date,
          y: +events[i].distance};
      });
      const weeklyData = fillUpWeeks(createWeeklyAggregates(dailyData));

      const checkbox = document.getElementById('aggregate_checkbox');

      checkbox.addEventListener('change', (event) => {
        // First get rid off previous visalization.
        const svg = document.querySelector('svg');
        const children = Array.from(svg.childNodes);
        children.forEach((child) =>
          child.parentNode.removeChild(child)
        );

        const data = selectDataSet(event.target.checked, dailyData, weeklyData);
        displayData(data);
      });

      const data = selectDataSet(checkbox.checked, dailyData, weeklyData);
      displayData(data);
    }
  });
}
