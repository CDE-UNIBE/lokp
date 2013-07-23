<%def name="height()">500</%def>
<%def name="defaultWidth()">800</%def>

<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Charts - Overview</%def>

<%def name="head_tags()">

<style type="text/css" >
    #loadingRow {
        margin-bottom: 5px;
        background: url(/static/img/ajax-loader-green.gif) no-repeat center center;
    }
    .axis path,
    .axis line {
        fill: none;
        stroke: #000;
        shape-rendering: crispEdges;
    }
    .bar {
        fill: #A3A708;
    }
    .bar:hover {
        fill: #DBDB9B;
    }

    .valueShape {
        fill: #A3A708;
        stroke: darkGrey;
    }

    .valueText {
        fill: white;
    }
</style>
</%def>

<div class="container">
    <div class="content no-border">

        <div class="row-fluid">
            <div class="pull-right">
                <ul class="nav nav-pills">
                    % for g in groupableBy:
                    <li
                        % if g == groupedBy:
                        class="active"
                        % endif
                        ><a href="?groupby=${g}">${g}</a></li>
                    % endfor
                </ul>
            </div>
            
        </div>


        <h4>${groupedBy}</h4>

        <div id="loadingRow" class="row-fluid">
            <div class="span12">
                <div id="graphLoading" style="height: ${height()}px;"></div>
            </div>
        </div>

        <div id="graph"></div>

        <div class="btn-group" data-toggle="buttons-radio">
            <button class="btn" id="sortDesc">
                <i class="icon-sort-by-attributes-alt"></i>&nbsp;Sort desc
            </button>
            <button class="btn" id="sortAsc">
                <i class="icon-sort-by-attributes-alt"></i>&nbsp;Sort asc
            </button>
        </div>

        <div class="btn-group" data-toggle="buttons-radio">
            <button class="btn active" id="showCount">
                Count
            </button>
            <button class="btn" id="showSum">
                Sum
            </button>
        </div>

    </div>
</div>

<%def name="bottom_tags()">
<script src="http://d3js.org/d3.v3.min.js" type="text/javascript"></script>
<script type="text/javascript">
    // Calculate the dimensions of the graph
    width = ${defaultWidth()};
    height = ${height()};
    var contentEl = $('.content');
    if (contentEl.length) {
        width = contentEl.width();
    }

    labelKey = '${groupedBy}';

    valueKey1 = 'Activity (count)';
    valueKey2 = 'Intended area (ha) (sum)';

    // Load data and pass it to visualizing function
    var url = '/evaluation/1?groupby=' + labelKey;
    d3.json(url, function(error, json) {
	if (error) return console.warn(error);
	data = json;
        $('#loadingRow').hide();
	visualize(data);
    });
</script>
<script src="${request.static_url('lmkp:static/v2/charts/barchart.js')}" type="text/javascript"></script>

</%def>