var countryData = {};

/**
 * Size constants
 */
var width = 938,  // Relevant for ratio width/height
    height = 500; // Relevant for ratio width/height


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
 * Function to create the actual chart.
 */
function visualize(data) {

  var container_width = $("#map").width();
  var maxValue = 0;

  var projection = d3.geo.mercator()
    .scale(150)
    .translate([width / 2, height / 1.5]);

  var path = d3.geo.path()
    .projection(projection);

  var svg = d3.select("#map").append("svg")
    .attr("preserveAspectRatio", "xMidYMid")
    .attr("viewBox", "0 0 " + width + " " + height)
    .attr("width", container_width)
    .attr("height", container_width * height / width);

  svg.append("rect")
    .attr("class", "map-background")
    .attr("width", width)
    .attr("height", height);

  var countries_g = svg.append("g")
    .attr("id", "countries");

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

  d3.json("/static/v2/charts/world.topo.json", function(error, us) {

    $('#loading-div').hide();
    $('#helptext').show();

    countries_g.selectAll("path")
      .data(topojson.feature(us, us.objects.countries).features)
      .enter()
      .append("path")
      .attr("id", function(d) { return d.id; })
      .attr("d", path)
      .style('fill', function(d) {
        var c = d.id;
        if (c in countryData) {
          return quantize(countryData[c].value);
        }
      })
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
 * Create a list with all countries colored on the map.
 */
function populateCountriesList() {
  for (var v in countryData) {
    var x = $('<li/>', {
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

function unhighlightCountry() {
  d3.selectAll('#countries path')
    .classed('active', false);
  $('.countries-list-entry').each(function() {
    $(this).toggleClass('active', false);
  });
  $('#country-details').html('');
  $('#helptext').show();
}
