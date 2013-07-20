var data, currentKey, width;

function visualize(data) {

    data = data.data;

    var valueKey1 = 'Activity (count)';
    var labelKey = 'Intention of Investment';
    var valueKey2 = 'Intended area (ha) (sum)';
    currentKey = valueKey1;

    // Some size constants
    var chartPaddingTop = 50;
    var chartPaddingRight = 0;
    var chartPaddingBottom = 150;
    var chartPaddingLeft = 100;
    var fontSize = 10;
    var labelOffset = 25

    // Calculate sizes
    var chartBottom = height - chartPaddingBottom;
    var chartRight = width - chartPaddingRight;

    // Define Y scale and axis
    var yScale = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return d[currentKey]; })])
        .range([chartBottom, chartPaddingTop])
        .nice();
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient('left')
        .tickPadding(5)

    // Define X scale and axis
    var xScale = d3.scale.ordinal()
        .domain(data.map(function(d) { return d[labelKey] }))
        .rangeRoundBands([chartPaddingLeft + labelOffset, chartRight], 0.1);
    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient('bottom')
        .tickSize(0);

    // Create the graph
    var svg = d3.select("#graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height)

    // Create bars
    svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', function(d) { return xScale(d[labelKey]); })
        .attr('y', function(d) { return yScale(d[currentKey]); })
        .attr('width', xScale.rangeBand())
        .attr('height', function(d) { return chartBottom - yScale(d[currentKey]); })
        .attr('class', 'bar')
        .on('mouseover', function(d) {
            showValue(d);
        })
        .on('mouseout', function(d) {
            hideValue();
        });

    // Create the Y axis
    svg.append('g')
        .attr('class', 'axis yAxis')
        .attr('transform', 'translate(' + chartPaddingLeft + ', 0)')
        .call(yAxis)
        .append('text')
        .attr('y', fontSize + 5)
        .attr('x', -(height/2)+chartPaddingTop)
        .attr("transform", "rotate(-90)")
        .style('font-weight', 'bold')
        .style('text-anchor', 'middle')
        .attr('class', 'yAxisLabel')
        .text(currentKey)

    // Create the X axis
    svg.append('g')
        .attr('class', 'axis xAxis')
        .attr('transform', 'translate(0, ' + chartBottom + ')')
        .call(xAxis)
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('transform', 'translate(1, 2) rotate(-65)');

    svg.append('g')
        .attr('class', 'axis xAxis')
        .attr('transform', 'translate(0, ' + chartBottom + ')')
        .append('path')
        .attr('d', 'M' + chartPaddingLeft + ',0V0H' + (chartPaddingLeft + labelOffset) + 'V0')

    // Initial sort direction
    var sortDir = 'asc';

    // Use button to sort the graph
    d3.select('button#sortButton')
        .on('click', function() {
            sortChart();
        });

    //
    d3.select('button#changeData')
        .on('click', function() {
            changeData();
        });

    /**
     * Function to show the value of a bar.
     */
    var showValue = function(d) {

        var vHeight = 30;
        var vPadding = 10;

        svg.append('rect')
            .attr('x', xScale(d[labelKey]))
            .attr('y', yScale(d[currentKey]) - vPadding - vHeight)
            .attr('width', xScale.rangeBand())
            .attr('height', vHeight)
            .attr('class', 'valueShape')
        svg.append('text')
            .text(d[currentKey])
            .attr('x', xScale(d[labelKey]) + xScale.rangeBand() / 2)
            .attr('y', yScale(d[currentKey]) - vPadding - (vHeight / 2) + (fontSize / 2))
            .style('text-anchor','middle')
            .attr('class', 'valueText');

    }

    /**
     * Function to hide the value of a bar.
     */
    var hideValue = function() {
        svg.select('rect.valueShape').remove();
        svg.select('text.valueText').remove();
    }

    /**
     * Function to sort the chart.
     */
    var sortChart = function() {

        // Draw the newly sorted chart
        svg.selectAll('rect')
            .sort(function(a, b) {
                if (sortDir == 'asc') {
                    return d3.ascending(a[currentKey], b[currentKey]);
                } else {
                    return d3.descending(a[currentKey], b[currentKey]);
                }
            })
            .transition()
            .delay(function(d, i) {
                return i * 50;
            })
            .duration(1000)
            .attr('x', function(d, i) {
                return xScale(i);
            });

        // Store the new domain to update the scale
        var newDomain = [];
        svg.selectAll('rect')
            .each(function(d) {
                newDomain.push(d[labelKey]);
            });
        xScale.domain(newDomain);

        // Draw the axis again
        svg.select('.axis.xAxis')
            .transition()
            .duration(1000)
            .call(xAxis)
            .selectAll('text')
            .style('text-anchor', 'end')

        // Switch the sort direction
        sortDir = sortDir == 'asc' ? 'desc' : 'asc';
    }

    /**
     * Function to change the data of the chart (switches between valueKey1 and
     * valueKey2) and redraw it, also re-creating y-Axis.
     */
    var changeData = function() {
        // Switch the value key
        currentKey = (currentKey == valueKey1) ? valueKey2 : valueKey1;

        // Change the domain of the yScale
        yScale.domain([0, d3.max(data, function(d) { return d[currentKey]; })])

        // Update the bars
        svg.selectAll('rect')
        .transition()
        .delay(function(d, i) {
            return i * 50;
        })
        .attr('x', function(d) { return xScale(d[labelKey]); })
        .attr('y', function(d) { return yScale(d[currentKey]); })
        .attr('width', xScale.rangeBand())
        .attr('height', function(d) { return chartBottom - yScale(d[currentKey]); })
        .attr('class', 'bar')

        // Draw the axis again
        svg.select('.axis.yAxis')
            .transition()
            .duration(500)
            .call(yAxis)
            .selectAll('text')

        // Change axis label
        svg.select('text.yAxisLabel')
            .text(currentKey)

    }

}