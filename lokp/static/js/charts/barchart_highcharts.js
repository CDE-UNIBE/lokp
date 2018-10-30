function createBarChart(data, title, yAxisTitle, dataLabelFormat) {
    Highcharts.chart('container', {
        chart: {
            type: 'column'
        },
        title: {
            text: title
        },
        xAxis: {
            type: 'category'
        },
        yAxis: {
            title: {
                text: yAxisTitle
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    format: dataLabelFormat
                }
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
            pointFormat: '{point.name}: <b>' + dataLabelFormat + '<br/>'
        },
        "series": [
            {
                "name": title,
                "color": "#26a69a",
                "data": data
            }
        ]
    });
}

function prepareChartData(curr_key) {
    var new_data = responseData.data.map(function(d) {
        return {
            "name": d.group.value.default,
            "y": d.values[curr_key].value
        };
    }).filter(function(d) {
        if (excludeMyanmarData) {
            return d.name !== 'Myanmar';
        } else {
            return true;
        }
    }).sort(function(a, b) {
        return (a.y > b.y) ? -1 : ((b.y > a.y) ? 1 : 0);
    });

    var title = responseData.data[0]['group']['key']['default'];
    var yAxisTitle = attribute_names[curr_key];

    var dataLabelFormat = (curr_key === 0) ? '{point.y}' : '{point.y:,.2f} ha';
    createBarChart(new_data, title, yAxisTitle, dataLabelFormat);
}

function initContent(attr_names) {
    // Attribute select (radio)
    for (var i=0; i<attr_names.length; i++) {
        var attr = attr_names[i];
        var checked = (i === 0) ? 'checked' : '';
        var radio = '<p>' +
            '<input class="with-gap" name="attribute-select" type="radio" id="attribute-select-' + i + '" onclick="prepareChartData(' + i + ')" ' + checked + '/><label for="attribute-select-' + i + '">' + attr + '</label></p>';
        $('#attribute-buttons').append(radio);
    }

    // Group dropdown
    var groupable = responseData.translate.keys.map(function(k) {
        return k[0].default
    });
    for (var j=0; j<groupable.length; j++) {
        var name = groupable[j];
        var css_class = (j.toString() === group_key) ? 'active' : '';
        var li = '<li class="' + css_class + '"><a href="?attr=' + j + '">' + name + '</a></li>';
        $('#group-dropdown').append(li);
    }

    // Group dropdown title
    $('#group-dropdown-title').html(groupable[group_key]);
}
