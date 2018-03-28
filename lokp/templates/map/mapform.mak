<%page args="readonly=False, compare=False, identifier=None, version=None" />

<script type="text/javascript"
        src="//maps.googleapis.com/maps/api/js?v=3&key=${str(request.registry.settings.get('lokp.google_maps_api_key'))}&libraries=places"></script>
% if compare is True:
    <script src="${request.static_url('lokp:static/js/maps/compare.js')}" type="text/javascript"></script>
% else:
    <script src="${request.static_url('lokp:static/js/maps/form.js')}" type="text/javascript">
    </script>

% endif
## Scripts are only loaded when readonly is true to avoid conflict with dependencies provided by mapWidget (defined in config/form.py)
% if readonly:
    <script src="${request.static_url('lokp:static/lib/leaflet/leaflet.js')}" type="text/javascript"></script>
    <script src="${request.static_url('lokp:static/lib/leaflet/leaflet.markercluster.js')}"
            type="text/javascript"></script>
    <script src="${request.static_url('lokp:static/lib/leaflet/Leaflet.GoogleMutant.js')}"
            type="text/javascript"></script>
    <script src="/app/view/map_variables.js" type="text/javascript"></script>
    <script src="${request.static_url('lokp:static/lib/chroma/chroma.min.js')}" type="text/javascript"></script>
    <script src="${request.static_url('lokp:static/js/maps2/base.js')}" type="text/javascript"></script>
% endif


<script src="${request.static_url('lokp:static/lib/jquery.cookie/jquery.cookie.min.js')}"
        type="text/javascript"></script>


<script type="text/javascript">

        <%
            from lokp.config.customization import getOverviewKeys
            from lokp.views.filter import getFilterValuesForKey
            from lokp.views.map import getMapSymbolKeys
            from lokp.views.form import form_geomtaggroups
            import json

            aKeys, shKeys = getOverviewKeys(request)
            mapSymbols = getMapSymbolKeys(request)
            mapCriteria = mapSymbols[0]
            mapSymbolValues = [v[0] for v in sorted(getFilterValuesForKey(request,
            predefinedType='a', predefinedKey=mapCriteria[1]),
            key=lambda value: value[1])]
            geomTaggroups = form_geomtaggroups(request)
        %>

    var bbox = null;
    var coordsSet = false;
        ##  passing variables to javascript
                % if geometry and readonly:
                            coordsSet = true;
                    var geometry = ${geometry | n};
                            ## | applies escape filter, see http://docs.makotemplates.org/en/latest/filtering.html
                    var dealAreas = ${dealAreas | n};
                            var zoomlevel = 13;
                            ##     % elif '_LOCATION_' in request.cookies:
                    ##         ## Try to get the coordinates from the _LOCATION_ cookie
                    ##         var location_cookie = $.cookie('_LOCATION_');
                    ##         if (location_cookie) {
                    ##             var bbox_arr = location_cookie.split(',');
                    ##             if (bbox_arr.length == 4) {
                    ##                 var bbox = new OpenLayers.Bounds(bbox_arr);
                    ##             }
                    ##         }

                            // TODO: pass geometries for compare here

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
    var areaNames = ${json.dumps(geomTaggroups['mainkeys']) | n};
    var allMapCriteria = ${json.dumps(mapSymbols) | n};

    if ("custom_area_names" in window) {
        if (areaNames.length == custom_area_names.length) {
            for (var i = 0; i < areaNames.length; i++) {
                areaNames[i][0] = custom_area_names[i];
            }
        }
    }

        % if compare is True:
            ##  TODO: remove this codeblock (is not called in compare)

            var tForChangesInThisSection = '${_("There are changes in this section")}';
            ##  var geometry = ${geometry | n};
        % endif

</script>
