<%def name="height()">500</%def>
<%def name="defaultWidth()">800</%def>

<%inherit file="lmkp:customization/lo/templates/base.mak" />

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

    ul.chartNav li a {
        color: #333333;
    }
    ul.chartNav li a:hover {
        background-color: #DBDB9B;
    }
    ul.chartNav li.active a {
        background-color: #A3A708;
        color: #white;
    }
    ul.chartNav li.active a:hover {
        background-color: #A3A708;
    }
</style>
</%def>

<div class="container">
    <div class="content no-border">

        % if alert:
        <div class="alert alert-info">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <strong>Please stay tuned!</strong> We will be adding more visualizations soon.
        </div>
        % endif

        <div class="row-fluid">
            <div class="pull-right">
                <ul class="nav nav-pills chartNav">
                    % for g in groupableBy:
                    <li
                        % if g == groupedBy:
                        class="active"
                        % endif
                        ><a href="?groupby=${g}" data-toggle="tooltip" title="Group deals by ${g}">${g}</a></li>
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

        <div id="graph"><!-- Placeholder --></div>

        <div class="row-fluid">
            <div class="span6">
                <div class="btn-group" data-toggle="buttons-radio">
                    <button class="btn active" id="showCount" data-toggle="tooltip" title="Show the number of deals">
                        #&nbsp;Deals
                    </button>
                    <button class="btn" id="showSum" data-toggle="tooltip" title="Show the sum of the Intended area">
                        &Sigma;&nbsp;Area
                    </button>
                </div>
            </div>
            <div class="span6 text-right">
                <div class="btn-group" data-toggle="buttons-radio">
                    <button class="btn" id="sortDesc" data-toggle="tooltip" title="Sort data descending">
                        <i class="icon-sort-by-attributes-alt"></i>
                    </button>
                    <button class="btn" id="sortAsc" data-toggle="tooltip" title="Sort data ascending">
                        <i class="icon-sort-by-attributes"></i>
                    </button>
                </div>
            </div>
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

    valueKey1 = 'Deals (count)';
    valueKey2 = 'Intended area (ha) (sum)';

    // Load data and pass it to visualizing function
    var url = '/evaluation/1?groupby=' + labelKey;
    d3.json(url, function(error, json) {
	if (error) return console.warn(error);
	data = json;
        $('#loadingRow').hide();
	visualize(data);
    });

    /**
     * Initialize all bootstrap tooltips.
     * https://github.com/twitter/bootstrap/issues/5687#issuecomment-14917403
     */
    $(function () {
        // Tooltips for buttons are placed at the top
        $("button[data-toggle='tooltip']").tooltip({
            container: 'body'
        });
        // Tooltips for links are place at the bottom
        $("a[data-toggle='tooltip']").tooltip({
            container: 'body',
            placement: 'bottom'
        });
    });
</script>
<script src="${request.static_url('lmkp:static/v2/charts/barchart.js')}" type="text/javascript"></script>

</%def>