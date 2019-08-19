// Array of API discovery doc URLs for APIs used by the quickstart
const DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"];

// Authorization scopes required by the API; multiple scopes can be
// included, separated by spaces.
const SCOPES = "https://www.googleapis.com/auth/calendar.readonly";

const authorizeButton = document.getElementById('authorize_button');
const signoutButton = document.getElementById('signout_button');

var state = true;

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
  var pre = document.getElementById('content');
  var textContent = document.createTextNode(message + '\n');
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
    scope: SCOPES
  }).then(function () {
    // Listen for sign-in state changes.
    gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);

    // Handle the initial sign-in state.
    updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
    authorizeButton.onclick = handleAuthClick;
    signoutButton.onclick = handleSignoutClick;
  }, function(error) {
    appendPre(JSON.stringify(error, null, 2));
  });
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
  const svg = document.querySelector('svg');
  const children = Array.from(svg.childNodes);
  children.forEach((child) =>
    child.parentNode.removeChild(child)
  )
  displayEvents(state);
}

/**
 * Print the summary and start datetime/date of the next ten events in
 * the authorized user's calendar. If no events are found an
 * appropriate message is printed.
 */
function displayEvents(use_aggregate) {

  gapi.client.calendar.events.list({
    'calendarId': 'primary',
    'timeMin': (new Date(2016, 9, 10)).toISOString(),
    'timeMax': (new Date()).toISOString(),
    'showDeleted': false,
    'singleEvents': true,
    'maxResults': 10000,
    'orderBy': 'startTime'
  }).then(function(response) {

    // Filter and process calendar events.
    let events = response.result.items;
    if (events.length > 0) {
      events = events.filter(x => x.summary == 'Running');
      events = events.filter(x => typeof x.description !== 'undefined');
      for (i = 0; i < events.length; i++) {
        var event = events[i];
        event.date = extractDate(event);
        event.distance = event.description.split(" ")[0];
      }

      var data = d3.range(events.length).map(i => {
        return {x: events[i].date,
                y: +events[i].distance}
      })

      if (use_aggregate) {
        data = d3.nest()
          .key(function(d){
            return d3.timeWeek(d.x);
          })
          .rollup(function(leaves){
            return d3.sum(leaves, function(d) {return (d.y)});
          })
          .entries(data)
          .map(function(datum) {
            return {
              x: new Date(datum.key),
              y: datum.value,
            }
          })
      }

      const svg = d3.select("svg"),
          margin = {top: 20, right: 20, bottom: 30, left: 40},
          width = +svg.attr("width") - margin.left - margin.right,
          height = +svg.attr("height") - margin.top - margin.bottom;

      const translation = "translate(" + margin.left + "," + margin.top
          + ")";

      const x = d3.scaleTime()
          .domain([new Date(2016, 9, 10), new Date()])
          .range([0, width]);

      const y = d3.scaleLinear()
          .domain(d3.extent(data, d => d.y))
          .range([height, 0]);

      const xAxis = d3.axisBottom(x),
          yAxis = d3.axisLeft(y);

      const zoom = d3.zoom()
          .scaleExtent([1, 32])
          .translateExtent([[0, 0], [width, height]])
          .extent([[0, 0], [width, height]])
          .on("zoom", zoomed);

      const line = d3.line()
          .defined(function(d) { return d; })
          .x(function(d) { return x(d.x); })
          .y(function(d) { return y(d.y); });

      // Define the area of the svg that can be 'used' and will not be
      // clipped.
      svg.append("defs").append("clipPath")
        .attr("transform", translation)
          .attr("id", "clip")
          .append("rect")
          .attr("width", width)
          .attr("height", height);

      var tip = svg.append('div')
       .attr('class', 'p')
       .html('I am a tooltip...')
       .style('border', '1px solid steelblue')
       .style('padding', '5px')
       .style('position', 'absolute')
       .style('display', 'none')
       .on('mouseover', function(d, i) {
         tip.transition().duration(0);
       })
       .on('mouseout', function(d, i) {
         tip.style('display', 'none');
       });

      // Define child of svg that will actually contain elements.
      const g = svg.append("g")
          .attr("transform", translation);

      g.append("g")
          .attr("class", "axis axis--x")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      g.append("g")
          .attr("class", "axis axis--y")
          .call(yAxis);

      g.append('g')
          .attr("clip-path", "url(#clip)")
          .selectAll(".circle")
          .data(data)
          .enter().append("circle")
          .attr("class", "datapoint")
          .attr("cx", function(d) {return x(d.x)})
          .attr("cy", function(d) {return y(d.y)})
          .attr("r", 3.5)
          .on('mouseout', function(d, i) {
              tip.transition()
              .delay(500)
              .style('display', 'none');
          })

      // This rect is only meant to trigger zoom/pan events.
      svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all")
        .attr('transform', translation)
        .call(zoom);



      function zoomed() {
        const t = d3.event.transform;
        const xt = t.rescaleX(x);
        g.select(".axis--x").call(xAxis.scale(xt));
        g.selectAll('circle')
          .attr('cx', function(d) {return xt(new Date(d.key))});
      }
    }
  });
}
