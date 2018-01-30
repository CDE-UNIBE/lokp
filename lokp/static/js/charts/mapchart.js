var svg;
var countryData = {};


/**
 * Size constants
 */
var width = 938,  // Relevant for ratio width/height
    height = 500; // Relevant for ratio width/height


/**
 * Function to draw the basic map without colors.
 */
function drawMap() {
  var container_width = $("#map").width();

  var projection = d3.geo.mercator()
    .scale(150)
    .translate([width / 2, height / 1.5]);

  var path = d3.geo.path()
    .projection(projection);

  $('#loading-div').hide();
    $('#helptext').show();

  svg = d3.select("#map").append("svg")
    .attr("preserveAspectRatio", "xMidYMid")
    .attr("viewBox", "0 0 " + width + " " + height)
    .attr("width", container_width)
    .attr("height", container_width * height / width);

  var countries_g = svg.append("g")
    .attr("id", "countries");

  var loading_g = svg.append('g')
    .attr('id', 'map-loading');

  loading_g.append('rect')
    .attr('width', width)
    .attr('height', height);

  var spinnerSize = 50;
  loading_g.append("svg:image")
    .attr('x', width / 2 - spinnerSize / 2)
    .attr('y', height / 2 - spinnerSize / 2)
    .attr('width', spinnerSize)
    .attr('height', spinnerSize)
    .attr("xlink:href","/custom/img/ajax-loader.gif");

  d3.json(map_url, function(error, us) {

    countries_g.selectAll("path")
      .data(topojson.feature(us, us.objects.countries).features)
      .enter()
      .append("path")
      .attr("id", function(d) { return d.id; })
      .attr("d", path)
      .classed('hover_country', function(d) {
        return d.id in countryData;
      })
      .on('mouseover', function(d, i) {
        if (d.id in countryData) {
          highlightCountry(d.id);
        }
      })
      .on('mouseout', function() {
        unhighlightCountry();
      });
  });

  $(window).resize(function() {
    var w = $("#map").width();
    svg.attr("width", w);
    svg.attr("height", w * height / width);
  });
}


/**
 * Function to update the HTML content on the page with parts of the
 * data once it is loaded.
 */
function updateContent(data) {

  var groupable = chartData['translate']['keys'];

  if (data.translate && data.translate.keys) {
    var groupable = data.translate.keys;
  }

  $('.chart-title').html(groupable[0][0].default);
}


/**
 * Function called when changing the profile.
 */
function changeProfile(profile) {
  d3.select('#map-loading').classed('hidden', false);
  chartData['profile'] = profile;
  loadMapData();
}


/**
 * Function to load the data.
 */
function loadMapData() {
  d3.xhr(data_url)
    .header('Content-Type', 'application/json')
    .post(
      JSON.stringify(chartData), function (error, rawData) {
        var data = JSON.parse(rawData.responseText);
        if (!data['success']) {
          return console.warn(data['msg']);
        }
        updateContent(data);
        colorMap(data.data);
      }
    );
}


/**
 * Function to create the actual chart.
 */
function colorMap(data) {

  var maxValue = 0;
  countryData = {};

  data.forEach(function(d) {
    var code = d.group.value.code;
    var count = d.values[0].value;
    var name = d.group.value.default;
    countryData[code] = {
      'value': count,
      'name': name
    };
    maxValue = Math.max(maxValue, count);
  });
  populateCountriesList();

  var quantize = d3.scale.quantize()
    .domain([0, maxValue])
    .range(colorbrewer.YlOrRd[9].slice(2));

  d3.select('#countries').selectAll('path')
    .style('fill', function(d) {
      var c = d.id;
      if (c in countryData) {
        return quantize(countryData[c].value);
      } else {
        return '#cde';
      }
    });

  d3.select('#map-loading').classed('hidden', true);
}


/**
 * Create a list with all countries colored on the map.
 */
function populateCountriesList() {
  $('#countries-list').html('');
  for (var v in countryData) {
    $('<li/>', {
      html: [
        countryData[v].name,
        '<span class="pull-right visible-phone">',
        countryData[v].value,
        '</span>'
      ].join(''),
      class: 'countries-list-entry'
    }).data('code', v).appendTo('#countries-list');
  }
  $('.countries-list-entry').on('mouseover', function() {
    highlightCountry($(this).data('code'));
  }).on('mouseout', function() {
    unhighlightCountry();
  });
  var countriesList = $('#countries-list');
  if (countriesList.height() > 300) {
    countriesList.css({
      'max-height': '300px',
      'overflow-y': 'scroll'
    });
  }
}


/**
 * Highlight a country when selected on the map or in the list.
 */
function highlightCountry(code) {
  d3.select('#countries path#' + code)
    .classed('active', true);
  $('.countries-list-entry').each(function() {
    if ($(this).data('code') == code) {
      $(this).toggleClass('active', true);
    }
  });
  $('#helptext').hide();
  $('#country-details').html([
    '<h2>' + countryData[code].name + '</h2>',
    '<p>' + attributeNames[0] + ': ' + countryData[code].value + '</p>'
  ].join(''));
}


/**
 * Unhighlight everything.
 */
function unhighlightCountry() {
  d3.selectAll('#countries path')
    .classed('active', false);
  $('.countries-list-entry').each(function() {
    $(this).toggleClass('active', false);
  });
  $('#country-details').html('');
  $('#helptext').show();
}
