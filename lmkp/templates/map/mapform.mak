<%page args="readonly=False" />

<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
<script src="${request.static_url('lmkp:static/lib/OpenLayers-2.12/OpenLayers.js')}" type="text/javascript"></script>
<script type="text/javascript" src="${request.route_url('context_layers')}"></script>
<script src="${request.static_url('lmkp:static/v2/maps/form.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/maps/base.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/jquery.cookie.js')}" type="text/javascript"></script>

<script type="text/javascript">

    <%
        from lmkp.views.views import getMapSymbolKeys
        from lmkp.views.views import getOverviewKeys
        from lmkp.views.views import getFilterValuesForKey
        import json

        aKeys, shKeys = getOverviewKeys(request)
        mapSymbols = getMapSymbolKeys(request)
        mapCriteria = mapSymbols[0]
        mapSymbolValues = [v[0] for v in sorted(getFilterValuesForKey(request,
            predefinedType='a', predefinedKey=mapCriteria[1]),
            key=lambda value: value[1])]
    %>

    var bbox = null;
    var coordsSet = false;
    % if geometry:
        var coordsSet = true;
        var geometry = ${geometry | n};
        var zoomlevel = 13;
    % elif '_LOCATION_' in request.cookies:
        ## Try to get the coordinates from the _LOCATION_ cookie
        var location_cookie = $.cookie('_LOCATION_');
        if (location_cookie) {
            var bbox_arr = location_cookie.split(',');
            if (bbox_arr.length == 4) {
                var bbox = new OpenLayers.Bounds(bbox_arr);
            }
        }
    % endif

    % if readonly:
        var readonly = true;
    % else:
        var readonly = false;
        var editmode = '${editmode}';
    % endif

    var aKeys = ${json.dumps(aKeys) | n};
    var shKeys = ${json.dumps(shKeys) | n};
    var mapValues = ${json.dumps(mapSymbolValues) | n};
    var mapCriteria = ${json.dumps(mapCriteria) | n};

    var tForDealsGroupedBy = '${_("Map symbols are based on")}';

</script>
