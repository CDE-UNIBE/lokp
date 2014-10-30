var data, svg, xScale, xAxis, yScale, yAxis;

var current_key = 0;
var minimizeLegend = false;

/**
 * Size constants
 */
var fontSize = 10,
    aspectRatio = 0.7, // Default ratio of width * height
    minOuterHeight = 500,
    legendMargin = 50,
    legendSymbolSize = 16;

/**
 * Initial sizes needed by d3 to create the chart. These will be
 * (partly) overwritten.
 */
var margin = {top: 50, right: 0, bottom: 0, left: 100},
    outerWidth = 100,
    innerWidth = 50,
    outerHeight = 100,
    innerHeight = 50;

function updateContent(data) {

  var groupable = chart_data['translate']['keys'];
  if (data.translate && data.translate.keys) {
    groupable = data.translate.keys;
  }

  // Group by buttons
  if (groupable.length > 1) {
    var group_by_html = [];
    for (var i=0; i<groupable.length; i++) {
      var css_class = '';
      if (i == group_key) {
        css_class = 'active';
      }
      group_by_html.push([
        '<li class="', css_class, '"><a href="?attr=', i, '" ',
        'data-toggle="tooltip" ',
        'title="', group_activities_by, ' ', groupable[i][1].default + ' / ' + groupable[i][0].default, '">',
        groupable[i][1].default + ' / ' + groupable[i][0].default,
        '</a></li>'
      ].join(''));
    }
    $('#group-by-pills').html(group_by_html.join(''));
  }

  // Attribute buttons
  if (attribute_names.length > 1) {
    var attribute_html = [];
    for (var i=0; i<attribute_names.length; i++) {
      var css_class = '';
      if (i == 0) {
        css_class = ' active';
      }
      attribute_html.push([
        '<button class="btn change-attribute', css_class, '" ',
        'value="', i, '" data-toggle="tooltip" ',
        'title="', show_attribute, ' ', attribute_names[i], '">',
        attribute_names[i],
        '</button>'
      ].join(''));
    }
    $('#attribute-buttons').html(attribute_html.join(''));
  }

  // Title
  $('#group-by-title').html(groupable[group_key][1].default + ' / ' + groupable[group_key][0].default);
}


/**
 * (Re-)Calculate the dimensions of the chart.
 */
function calculateDimensions() {
  var marginBottom = 0;
  var xAxis = d3.selectAll('.xAxis');
  if (xAxis.node()) {
    var xAxisEntry = xAxis.selectAll('.tick');
    xAxisEntry[0].forEach(function(a) {
      marginBottom = Math.max(marginBottom, a.getBBox().height);
    });
  }
  margin = {
    top: margin.top,
    right: margin.right,
    bottom: marginBottom,
    left: margin.left
  };
  outerWidth = parseInt(d3.select('#chart').style('width'), 10);
  innerWidth = outerWidth - margin.left - margin.right;
  outerHeight = Math.max(
    parseInt(innerWidth * aspectRatio, 10), minOuterHeight);
  innerHeight = outerHeight - margin.top - margin.bottom;
}

/**
 * The main function to create the chart. Create the initial chart, then
 * recalculate the dimensions to make it fit the screen.
 */
function visualize(d) {

  data = d;

  // Prepare the Y scale and axis
  yScale = d3.scale.linear()
    .range([innerHeight, 0])
    .nice();
  yAxis = d3.svg.axis()
    .scale(yScale)
    .orient('left')
    .tickPadding(5);

  // Prepare the X scale and axis
  xScale = d3.scale.ordinal()
    .rangeRoundBands([0, innerWidth], 0.1, 0.3);
  xAxis = d3.svg.axis()
    .scale(xScale)
    .orient('bottom')
    .tickSize(0);

  // Add chart container
  svg = d3.select("#chart").append("svg")
    .attr("width", outerWidth)
    .attr("height", outerHeight)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Prepare color range
  var colorGroups = [];
  data.forEach(function(dataEntry) {
    dataEntry.children.forEach(function(d) {
      var groupLabel = getGroupLabel(d);
      if (colorGroups.indexOf(groupLabel) == -1) {
        if (groupLabel) {
          colorGroups.push(groupLabel);
        } else {
          colorGroups.unshift(groupLabel);
        }
      }
    })
  });
  var color = d3.scale.ordinal()
    .domain(colorGroups)
    .range(colorbrewer.Paired[colorGroups.length+1]);

  // Prepare the data
  data.forEach(function(dataEntry) {
    var y0 = 0;
    dataEntry.groups = color.domain().map(function(name) {
      var v = 0;
      dataEntry.children.forEach(function(d) {
        if (getGroupLabel(d) == name) {
          v = getGroupValue(d, current_key);
        }
      });
      return {
        name: name,
        y0: y0,
        y1: y0 += +v
      }
    });
    dataEntry.total = dataEntry.groups[dataEntry.groups.length - 1].y1;
  });

  // Sort the data and attach it to the scales
  data.sort(function(a, b) { return b.total - a.total; });
  xScale.domain(data.map(function(d) {
    return getGroupLabel(d);
  }));
  yScale.domain([0, d3.max(data, function(d) { return d.total; })]);

  // Add the groups which make the bars
  var groups = svg.selectAll(".groups")
      .data(data)
    .enter().append("g")
      .attr("class", "groups")
      .attr("transform", function(d) {
        return "translate(" + xScale(getGroupLabel(d)) + ",0)";
      });
  groups.selectAll("rect")
      .data(function(d) { return d.groups; })
    .enter().append("rect")
      .attr("width", xScale.rangeBand())
      .attr("y", function(d) {
        return yScale(d.y1);
      })
      .attr("height", function(d) {
        return yScale(d.y0) - yScale(d.y1);
      })
      .style("fill", function(d) {
        return color(d.name);
      })
      .on('mouseover', function(d, i, n) {
        showValues(n);
        highlightLegend(d.name);
      })
      .on('mouseout', function() {
        unhighlight();
      });

  // Add X Axis
  svg.append("g")
      .attr("class", "axis xAxis")
      .attr("transform", "translate(0," + innerHeight + ")")
      .call(xAxis)
    .selectAll('text')
      .style('text-anchor', 'end')
      .attr("transform", 'translate(-10, 2) rotate(-65)' )
      .on('mouseover', function(d, i) {
        showValues(i);
        highlightLegend();
        highlightBarsAll(i);
      })
      .on('mouseout', function() {
        unhighlight();
      });

  // Add Y Axis
  svg.append("g")
      .attr("class", "axis yAxis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .attr('class', 'yAxisLabel')
      .text(getYLabel(current_key));

  // Legend
  var legend = svg.append('g')
    .attr('id', 'legend')
    .attr('transform', 'translate(' + innerWidth + ', 0)');

  legend.append('rect')
    .attr('id', 'legend-container');

  legend.append('text')
    .attr('x', innerWidth - 8)
    .attr('id', 'legend-title')
    .style('text-anchor', 'end');

  var legendEntries = legend.selectAll(".legend-entry")
      .data(color.domain().slice().reverse())
    .enter().append("g")
      .attr("class", "legend-entry")
      .attr("transform", function(d, i) { return "translate(0," + (15 + (i * 20)) + ")"; })
      .on('mouseover', function(d, i) {
        highlightBars(d);
        highlightLegend(d);
      })
      .on('mouseout', function() {
        unhighlight();
      });

  legendEntries.append("rect")
      .attr("x", innerWidth - legendMargin)
      .attr("width", legendSymbolSize)
      .attr("height", legendSymbolSize)
      .style("fill", color);

  legendEntries.append("text")
      .attr("x", innerWidth - legendMargin - 8)
      .attr("y", 9)
      .attr("dy", ".35em")
      .attr('class', 'legend-label')
      .style("text-anchor", "end")
      .text(function(d) {
        return (d) ? d : translationForUnknown;
      });

  legendEntries.append('text')
    .attr('x', innerWidth - legendMargin + legendSymbolSize + 8)
    .attr('y', 9)
    .attr('dy', '.35em')
    .attr('class', 'legend-count');

  resize();

  var bbox = svg.selectAll('#legend').node().getBBox();
  svg.selectAll('#legend-container')
    .attr('x', bbox.x - 8)
    .attr('y', bbox.y + 8)
    .attr('width', Math.abs(bbox.x) + legendMargin + 8)
    .attr('height', bbox.height);

  // Responsive chart
  d3.select(window).on('resize', resize);
}

/*
 * Resize the chart.
 */
function resize() {
  unhighlight()
  calculateDimensions();

  // Update the chart container
  d3.select("#chart").select('svg')
    .attr("width", outerWidth)
    .attr("height", outerHeight);

  // Update X and Y scales and axis
  xScale.rangeRoundBands([0, innerWidth], 0.1, 0.3);
  yScale.range([innerHeight, 0]).nice();
  svg.select('.axis.xAxis')
    .attr("transform", "translate(0," + innerHeight + ")")
    .call(xAxis.orient('bottom'))
  .selectAll('text')
    .style('text-anchor', 'end')
  svg.select('.axis.yAxis')
    .call(yAxis);

  // Update the groups
  var groups = svg.selectAll('.groups')
    .attr('transform', function(d) {
      return "translate(" + xScale(getGroupLabel(d)) + ",0)";
    });

  // Update the bars
  groups.selectAll("rect")
      .attr("width", xScale.rangeBand())
      .attr("y", function(d) {
        return yScale(d.y1);
      })
      .attr("height", function(d) {
        return yScale(d.y0) - yScale(d.y1);
      });

  // Update the legend
  var x = svg.selectAll('#legend')
    .attr('transform', 'translate(' + (innerWidth - legendMargin) + ', 0)');

  minimizeLegend = false;
  var legend = d3.select('#legend');
  if (legend.node()) {
    var legend_rect = legend.node().getBoundingClientRect();
    var groups = d3.selectAll('.groups')
    groups[0].forEach(function(g) {
      var group_rect = g.getBoundingClientRect();
      if (group_rect.right > legend_rect.left && group_rect.top < legend_rect.bottom) {
        minimizeLegend = true;
      }
    });
  }
  svg.selectAll('#legend').classed('legend-small', minimizeLegend);
}
/**
 * Function to show the values of the groups of a bar by its index. Also
 * displays the name of the outer group.
 */
function showValues(index) {
  var dataEntry = data[index];
  svg.selectAll('.legend-count')
    .text(function(groupName, groupIndex) {
      var entry = dataEntry.groups[dataEntry.groups.length - groupIndex - 1];
      return entry.y1 - entry.y0;
    });
  svg.select('#legend-title')
    .text(getGroupLabel(dataEntry));
}

/**
 * Highlight a legend entry by name of the group. If no name is provided,
 * highlight all legend entries.
 */
function highlightLegend(groupName) {
  svg.selectAll('.legend-entry')
    .classed('active', function(legendEntry) {
      return legendEntry == groupName || (typeof groupName == 'undefined');
    });
  svg.selectAll('#legend-container')
    .classed('active', true);
}

/**
 * Highlight all groups of the bars with a certain name.
 */
function highlightBars(groupName) {
  svg.selectAll('.groups')
    .selectAll('rect')
      .classed('active', function(group) {
        return group.name == groupName;
      });
}

function highlightBarsAll(index) {
  svg.selectAll('.groups')
    .selectAll('rect')
      .classed('active', function(group, groupIndex, barIndex) {
        return barIndex == index;
      });
}

/**
 * Unhighlight everything. Empties legend (title, count) and deselects all
 * active objects.
 */
function unhighlight() {
  // Legend
  svg.selectAll('.legend-entry')
    .classed('active', false);
  svg.select('#legend-title')
  .text('');
  svg.selectAll('.legend-count')
    .text('');
  svg.selectAll('#legend-container')
    .classed('active', false);

  // Bars
  svg.selectAll('.groups')
    .selectAll('rect')
      .classed('active', false);
}

function getGroupValue(d, i) {
  return d.values[i].value;
}

function getYLabel(i) {
  return attribute_names[i];
}

function getGroupLabel(d) {
  return d.group.value.default;
}
