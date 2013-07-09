<%page args="readonly=False" />

<script src="${request.static_url('lmkp:static/lib/OpenLayers-2.12/OpenLayers.js')}" type="text/javascript"></script>
<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
<script src="${request.static_url('lmkp:static/v2/mapform.js')}" type="text/javascript"></script>

<script type="text/javascript">
    $(document).ready(function() {
    var layers = getBaseLayers();

    markerLayer = new OpenLayers.Layer.Markers("Points", {
        'calculateInRange': function() { return true; }
    });
    layers.push(markerLayer);

    var map = new OpenLayers.Map('googleMapNotFull', {
        displayProjection: geographicProjection,
        projection: sphericalMercatorProjection,
        controls: [
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.Navigation({
                dragPanOptions: {
                    enableKinetic: true
                }
            }),
            new OpenLayers.Control.PanZoom()
        ],
        layers: layers
    });

    var pointIsSet = false;
    var coords = [0, 0];
    var zoomlevel = 1;

    % if coords:
        pointIsSet = true;
        coords = ${coords};
        zoomlevel = 13;
    % endif
    var coordsTransformed = new OpenLayers.LonLat(coords[0], coords[1])
        .transform(geographicProjection,sphericalMercatorProjection);
    map.setCenter(coordsTransformed, zoomlevel);
    if (pointIsSet) {
        markerLayer.addMarker(getMarker(coordsTransformed));
    }

    % if not readonly:

        $('#googleMapNotFull').css('cursor', "crosshair");

        map.events.register('click', map, function(e) {
            var position = map.getLonLatFromPixel(e.xy);

            // Set a new marker on the map
            markerLayer.clearMarkers();
            markerLayer.addMarker(getMarker(position));

            // Store the new coordinates for form submission
            var coords = position.clone().transform(sphericalMercatorProjection, geographicProjection)
            var lon = $('input[name=lon]');
            if (lon && lon.length == 1) {
                $(lon[0]).val(coords.lon);
            }
            var lat = $('input[name=lat]');
            if (lat && lat.length == 1) {
                $(lat[0]).val(coords.lat);
            }

        });
    % endif

});
</script>
