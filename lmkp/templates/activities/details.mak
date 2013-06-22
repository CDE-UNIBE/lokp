<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Deal Details</%def>

<%def name="head_tags()">
    <script src="${request.static_url('lmkp:static/lib/OpenLayers-2.12/OpenLayers.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
    <style type="text/css" >
        .olTileImage {
            max-width: none !important;
        }
        /* Some nasty temporary css hacks */
        p.deal-detail {
            font-weight: normal;
        }
        .row-fluid [class*="span"]:first-child {
            margin-left: 10px;
        }
        .row-fluid [class*="span"] {
            margin-left: 10px;
        }
        .row-fluid [class*="span"]:first-child [class*="span"]:first-child h5 {
            color: #A3A708;
            font-weight: bold;
        }
        .row-fluid [class*="span"] h5 {
            font-weight: normal;
        }

    </style>
</%def>

<div class="container">
    <div class="content no-border">
        ${form | n}
    </div>
</div>

<%def name="bottom_tags()">
    <script src="${request.static_url('lmkp:static/v2/activitydetails.js')}" type="text/javascript"></script>

    <script type="text/javascript">
        $(document).ready(function() {
        var layers = getBaseLayers();

        markerLayer = new OpenLayers.Layer.Markers("Points")
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
                new OpenLayers.Control.PanZoomBar()
            ],
            layers: layers
        });

        % if coords:
            var coords = ${coords};
            var coordsTransformed = new OpenLayers.LonLat(coords[0], coords[1])
                .transform(geographicProjection,sphericalMercatorProjection);
            map.setCenter(coordsTransformed, 13);
            markerLayer.addMarker(getMarker(coordsTransformed));
        % endif

    });
    </script>

</%def>
