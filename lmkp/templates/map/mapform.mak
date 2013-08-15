<%page args="readonly=False" />

<script src="${request.static_url('lmkp:static/lib/OpenLayers-2.12/OpenLayers.js')}" type="text/javascript"></script>
<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
<script src="${request.static_url('lmkp:static/v2/mapform.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/jquery.cookie.js')}" type="text/javascript"></script>

<script type="text/javascript">

    % if coords:
        var pointIsSet = true;
        var coords = ${coords};
        var zoomlevel = 13;
    % else:
        var pointIsSet = false;
        ## Try to get the coordinates from the _LOCATION_ cookie
        % if '_LOCATION_' in request.cookies:
            var location_cookie = $.cookie('_LOCATION_');
            if (location_cookie) {
                var bbox_arr = location_cookie.split(',');
                if (bbox_arr.length == 4) {
                    var bbox = new OpenLayers.Bounds(bbox_arr);
                }
            }
        % endif
        ## Fallback: Show the whole world
        var coords = [0, 0];
        var zoomlevel = 1;
    % endif

    % if readonly:
        var readonly = true;
    % else:
        var readonly = false;
    % endif

</script>
