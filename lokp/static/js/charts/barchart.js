var data, svg, xScale, xAxis, yScale, yAxis;

var current_key = 0;

/**
 * Size constants
 */
var fontSize = 10,
    minOuterHeight = 500;

/**
 * Initial sizes needed by d3 to create the chart. These will be
 * (partly) overwritten.
 */
var margin = {top: 50, right: 0, bottom: 0, left: 100},
    aspectRatio = 0.7, // Ratio Width * Height
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
        'title="', group_activities_by, ' ', groupable[i][0].default, '">',
        groupable[i][0].default,
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
      } else {
        css_class = ' inactive';
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
  $('#group-by-title').html(groupable[group_key][0].default);
  $('#group-by-dropdown-title').html(groupable[group_key][0].default);

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
 * The main function to create the chart
 */
function visualize(data) {

  // Sizes
  calculateDimensions();

  // Define Y scale and axis
  yScale = d3.scale.linear()
    .domain([0, d3.max(data, function(d) {
      return getYValue(d, current_key);
    })])
    .range([innerHeight, 0])
    .nice();
  yAxis = d3.svg.axis()
    .scale(yScale)
    .orient('left')
    .tickPadding(5);

  // Define X scale and axis
  xScale = d3.scale.ordinal()
    .domain(data.map(function(d) {
      return getXValue(d);
    }))
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

  // Add bars
  svg.selectAll("bar")
    .data(data)
  .enter().append("rect")
    .attr("x", function(d) {
      return xScale(getXValue(d));
    })
    .attr("width", xScale.rangeBand())
    .attr("y", function(d) {
      return yScale(getYValue(d, current_key));
    })
    .attr("height", function(d) {
      return innerHeight - yScale(getYValue(d, current_key));
    })
    .attr('class', 'bar')
    .on('mouseover', function(d) {
      showValue(d);
    })
    .on('mouseout', function(d) {
      hideValue();
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

  // Add X Axis
  svg.append("g")
    .attr("class", "axis xAxis")
    .attr("transform", "translate(0," + innerHeight + ")")
    .call(xAxis)
  .selectAll("text")
    .style("text-anchor", "end")
    .attr("transform", 'translate(-10, 2) rotate(-65)' )
    .on('mouseover', function(d, i) {
      svg.selectAll("rect.bar")
        .classed("hover", function(e, j) { return getXValue(e) == d; });
      showValue(data[i]);
    })
    .on('mouseout', function(d) {
      svg.selectAll("rect.bar")
        .classed("hover", function(e, j) { return false; });
      hideValue();
    });

  // Enable Buttons
  $('a#sortAsc').click(function() {
    sortChart('asc');
    sortChart('asc');
  });
  $('a#sortDesc').click(function() {
    sortChart('desc');
    sortChart('desc');
  });
  $('button.change-attribute').click(function() {
    changeData($(this).attr('value'));
    $('button.change-attribute').addClass("inactive");
    $(this).removeClass("inactive");
  });

  resize();

  // Responsive chart
  d3.select(window).on('resize', resize);

  /**
   * Function to change the data of the chart
   */
  var changeData = function(key) {

    current_key = key;

    // Update Y scale, axis and label
    yScale.domain([0, d3.max(data, function(d) {
      return getYValue(d, current_key);
    })]);
    svg.select('.axis.yAxis')
      .transition()
      .duration(500)
      .call(yAxis)
      .selectAll('text');
    svg.select('text.yAxisLabel')
      .text(getYLabel(current_key));

    // Update the bars
    svg.selectAll('rect')
      .transition()
      .delay(function(d, i) {
        return i * 50;
      })
      .attr('x', function(d) {
        return xScale(getXValue(d));
      })
      .attr('y', function(d) {
        return yScale(getYValue(d, current_key));
      })
      .attr('width', xScale.rangeBand())
      .attr('height', function(d) {
        return innerHeight - yScale(getYValue(d, current_key));
      })
      .attr('class', 'bar');
  }
}

/*
 * Resize the chart.
 */
function resize() {
  hideValue();
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

  // Update the bars
  svg.selectAll('rect')
    .attr('x', function(d, i) {
      return xScale(getXValue(d));
    })
    .attr("width", xScale.rangeBand())
    .attr('height', function(d) {
      return innerHeight - yScale(getYValue(d, current_key));
    })
    .attr("y", function(d) {
      return yScale(getYValue(d, current_key));
    });
}

 /**
 * Function to sort the chart.
 */
function sortChart(sortDir) {

  // Update the X scale and axis
  var newDomain = [];
  svg.selectAll('rect')
    .each(function(d) {
      newDomain.push(getXValue(d));
    });
  xScale.domain(newDomain);
  svg.select('.axis.xAxis')
    .transition()
    .duration(1000)
    .call(xAxis)
  .selectAll('text')
    .style('text-anchor', 'end');

  // Update the bars
  svg.selectAll('rect')
    .sort(function(a, b) {
      if (sortDir == 'asc') {
        return d3.ascending(
          getYValue(a, current_key), getYValue(b, current_key));
      } else {
        return d3.descending(
          getYValue(a, current_key), getYValue(b, current_key));
      }
    })
    .transition()
    .delay(function(d, i) {
      return i * 50;
    })
    .duration(1000)
    .attr('x', function(d, i) {
      return xScale(getXValue(d));
    });
}

/**
 * Function to show the value of a bar.
 */
function showValue(d) {
  var vHeight = 30;
  var vPadding = 10;

  var valueShape = svg.append('rect');

  var valueText = svg.append('text');
  valueText
    .text(formatNumber(getYValue(d, current_key)))
    .attr('x', xScale(getXValue(d)) + xScale.rangeBand() / 2)
    .attr('y', yScale(getYValue(d, current_key)) - vPadding - (vHeight / 2)
      + (fontSize / 2))
    .style('text-anchor','middle')
    .attr('class', 'valueText');

  var valueTextBbox = valueText[0][0].getBBox();
  var textPadding = 5;

  valueShape
    .attr('x', Math.min(xScale(getXValue(d)), valueTextBbox.x-textPadding))
    .attr('y', yScale(getYValue(d, current_key)) - vPadding - vHeight)
    .attr('width', Math.max(xScale.rangeBand(), valueTextBbox.width+textPadding*2))
    .attr('height', vHeight)
    .attr('class', 'valueShape');
}

/**
 * Function to hide the value of a bar.
 */
function hideValue() {
  svg.select('rect.valueShape').remove();
  svg.select('text.valueText').remove();
}

/**
 * Helper function to return a nicely rendered number string (adds thousands
 * separator). Also round numbers to 2 decimal places.
 * http://stackoverflow.com/a/2646441/841644
 */
function formatNumber(nStr) {
  nStr += '';
  var x = nStr.split('.');
  var x1 = x[0];
  var x2 = x.length > 1 ? '.' + x[1] : '';
  if (x2) {
    x2 = parseFloat(x2).toFixed(2);
  }
  var rgx = /(\d+)(\d{3})/;
  while (rgx.test(x1)) {
    x1 = x1.replace(rgx, '$1' + ',' + '$2');
  }
  return x1 + x2;
}

function getYValue(d, i) {
  return d.values[i].value;
}

function getYLabel(i) {
  return attribute_names[i];
}

function getXValue(d) {
  return d.group.value.default;
}
