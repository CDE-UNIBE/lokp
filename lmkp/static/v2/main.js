var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");




window.onload = function() {

    var layers = getBaseLayers();

    var map = new OpenLayers.Map("map-div", {
        displayProjection: geographicProjection,
        controls: [
        new OpenLayers.Control.Attribution(),
        new OpenLayers.Control.Navigation({
            dragPanOptions: {
                enableKinetic: true
            }
        }),
        new OpenLayers.Control.PanZoom()
        ],
        layers: layers,
        eventListeners: {
            "moveend": function(event){
                var center = map.getCenter();
                var zoom = map.getZoom();
                $.cookie("_LOCATION_", center.lon + "|" + center.lat + "|" + zoom, {
                    expires: 7
                });
                var ext  = map.getExtent();
                activitiesLayer.protocol.read({
                    params: {
                        epsg: 900913,
                        bbox: ext.left + "," + ext.bottom + "," + ext.right + "," + ext.top,
                        limit: 500
                    },
                    url: "/activities/geojson"
                });
            }
        },
        projection: sphericalMercatorProjection
    });

    var fillOpacity = 0.6;

    var rules = [
    // Rule for active Activities
    new OpenLayers.Rule({
        title: "Active Activities",
        filter: new OpenLayers.Filter.Comparison({
            property: 'status',
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            value: 'active'
        }),
        symbolizer: {
            graphicName: "circle",
            pointRadius: 7,
            fillColor: "#bd0026",
            fillOpacity: fillOpacity,
            strokeColor: "#bd0026",
            strokeWidth: 1
        }
    }), new OpenLayers.Rule({
        title: "Pending Activities",
        filter: new OpenLayers.Filter.Comparison({
            property: 'status',
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            value: 'pending'
        }),
        symbolizer: {
            graphicName: "triangle",
            pointRadius: 7,
            fillColor: "#ffa07a",
            fillOpacity: fillOpacity,
            strokeColor: "#ff6100",
            strokeWidth: 1
        }
    })
    ];

    var radius = function(feature){
        return (Math.min(feature.attributes.count, 7) + 3) * 1.5;
    }

    var count = function(feature){
        return feature.attributes.count;
    }

    var activitiesLayer = new OpenLayers.Layer.Vector('Activities', {
        eventListeners: {
            "featureselected": function(event){
                var feature = event.feature;
                if(feature.cluster.length == 1){
                    var f = feature.cluster[0];
                    var activityId = f.data.activity_identifier;
                    var shortId = activityId.split("-")[0]
                    $("#deal-shortid-span").html('<a href="/activities/html/' + activityId + '"># ' + shortId + '</a>');
                    $("#taggroups-ul" ).empty();
                    $.get("/activities/json/" + activityId, function(r){
                        var a = r.data[0];
                        for(var i=0; i < a.taggroups.length; i++){
                            var tg = a.taggroups[i];
                            if(tg.main_tag){
                                $( "#taggroups-ul" ).append( "<li><p><span class=\"bolder\">" + tg.main_tag.key + ": </span>" + tg.main_tag.value + "</p></li>" );
                            }
                        }
                    });
                } else {
                    $("#deal-shortid-span").html('# ');
                    $("#taggroups-ul").empty();
                    $("#taggroups-ul").append("<li><p><span class=\"bolder\">" + feature.cluster.length + " deals selected:</span> Please zoom in to get details about a single deal.</p></li>" );
                }
            },
            "featureunselected": function(event){
                if(activitiesLayer.selectedFeatures.length == 0){
                    $("#deal-shortid-span").html("#");
                    $("#taggroups-ul" ).empty();
                    $("#taggroups-ul").html("<li><p>No deal selected.</p></li>");
                }
            }
        },
        filter: new OpenLayers.Filter.Comparison({
            property: 'status',
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            value: 'active'
        }),
        isBaseLayer: false,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
            20037508.34, 20037508.34),
        protocol: new OpenLayers.Protocol.HTTP({
            format: new OpenLayers.Format.GeoJSON({
                externalProjection: geographicProjection,
                internalProjection: sphericalMercatorProjection
            }),
            url: "/activities/geojson"
        }),
        sphericalMercator: true,
        strategies: [
        new OpenLayers.Strategy.Fixed(),
        new OpenLayers.Strategy.Cluster({
            distance: 30
        })
        ],
        /*styleMap: new OpenLayers.StyleMap({
            "default": new OpenLayers.Style({}, {
                rules: rules
            }),
            "select": new OpenLayers.Style({
                fillColor: '#00ffff',
                fillOpacity: 0.8,
                strokeColor: '#006666'
            })
        })*/
        styleMap: new OpenLayers.StyleMap({
            "default":new OpenLayers.Style({
                fontColor: "#ffffff",
                fontSize: "9px",
                label: "${count}",
                pointRadius: "${radius}",
                fillColor: "#bd0026",
                fillOpacity: 1, //fillOpacity,
                strokeColor: "#bd0026",
                strokeOpacity: 0.5,
                strokeWidth: 5
            }, {
                context: {
                    count: count,
                    radius: radius
                }
            }),
            "select": new OpenLayers.Style({
                fontColor: "#000000",
                fontSize: "9px",
                label: "${count}",
                pointRadius: "${radius}",
                fillColor: "#00ffff",
                fillOpacity: 1, //fillOpacity,
                strokeColor: "#00ffff",
                strokeOpacity: 0.5,
                strokeWidth: 5
            }, {
                context: {
                    count: count,
                    radius: radius
                }
            })
        })
    });

    var selectControl = new OpenLayers.Control.SelectFeature(activitiesLayer,{
        map: map
    /*onSelect: function(feature){
            if(feature.cluster.length == 1){
                var f = feature.cluster[0];
                var activityId = f.data.activity_identifier;
                var shortId = activityId.split("-")[0]
                $("#deal-shortid-span").html('<a href="/activities/html/' + activityId + '"># ' + shortId + '</a>');
                $("#taggroups-ul" ).empty();
                $.get("/activities/json/" + activityId, function(r){
                    var a = r.data[0];
                    for(var i=0; i < a.taggroups.length; i++){
                        var tg = a.taggroups[i];
                        $( "#taggroups-ul" ).append( "<li><p><span class=\"bolder\">" + tg.main_tag.key + ": </span>" + tg.main_tag.value + "</p></li>" );
                    }
                });
                $(".basic-data").fadeIn();
            } else {
                $("#deal-shortid-span").html('# ');
                $("#taggroups-ul").empty();
                $("#taggroups-ul").append("<li><p><span class=\"bolder\">" + feature.cluster.length + " deals selected:</span> Please zoom in to get details about a single deal.</p></li>" );
                $(".basic-data").fadeIn();
            }
        },
        onUnselect: function(feature){
            if(activitiesLayer.selectedFeatures.length == 0){
                $(".basic-data").fadeOut(400, function(){
                    $("#deal-shortid-span").html("#");
                    $("#taggroups-ul" ).empty();
                    $("#taggroups-ul").html("<li><p>Select a deal to get information.</p></li>")
                });
            }
        }*/
    });
    selectControl.activate();

    map.addControl(selectControl);
    
    map.addLayers(getOverlayLayers());
    map.addLayers([activitiesLayer]);


    var location = $.cookie("_LOCATION_");
    if(location){
        var arr = location.split("|");
        map.setCenter(new OpenLayers.LonLat(arr[0], arr[1]), arr[2]);
    }

    /* events */

    $(".baseMapOptions").change(function(event){
        var bl = map.getLayersByName(event.target.value)[0];
        if(bl) {
            map.setBaseLayer(bl);
        }
    });

    $(".input-top").click(function(event){
        var ol = map.getLayersByName(event.target.value)[0];
        if(ol){
            ol.setVisibility(event.target.checked);
        }
    });

    /*$(".filter_area_openclose > .pointer").click(function(event){
        console.log("here");
        $(".filter_area").hide();
    });*/

    $(".context-layers-description > i").click(function(event){
        // Do something
        });

}

/**
 *
 */
function getBaseLayers(){

    var layers = [new OpenLayers.Layer.OSM("streetMap", [
        "http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile4.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg"
        ],{
            attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
            isBaseLayer: true,
            sphericalMercator: true,
            projection: sphericalMercatorProjection,
            transitionEffect: "resize"
        })];

    // Try to get the Google Satellite layer
    try {
        layers.push(new OpenLayers.Layer.Google("satelliteMap", {
            type: google.maps.MapTypeId.HYBRID,
            numZoomLevels: 22
        }));

        layers.push(new OpenLayers.Layer.Google("terrainMap", {
            type: google.maps.MapTypeId.TERRAIN
        }));
    // else get backup layers that don't block the application in case there
    // is no internet connection.
    } catch(error) {
        layers.push(new OpenLayers.Layer.OSM("satelliteMap", [
            "http://oatile1.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile2.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile3.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile4.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg"
            ],{
                attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
                isBaseLayer: true,
                sphericalMercator: true,
                projection: new OpenLayers.Projection("EPSG:900913")
            }));
    }

    return layers;
}

function getOverlayLayers() {
    var layers = [ new OpenLayers.Layer.WMS("Accessibility","http://cdetux2.unibe.ch/geoserver/lo/wms",{
        epsg: 900913,
        format: "image/jpeg",
        layers: "accessability",
        transparent: true
    },{
        visibility: false,
        isBaseLayer: false,
        sphericalMercator: true,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
        opacity: 0.7
    }),
    new OpenLayers.Layer.WMS("PopulationDensity2008","http://cdetux2.unibe.ch/geoserver/lo/wms",{
        epsg: 900913,
        format: "image/jpeg",
        layers: "lspop_2008",
        transparent: true
    },{
        visibility: false,
        isBaseLayer: false,
        sphericalMercator: true,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
        opacity: 0.6
    }),
    new OpenLayers.Layer.WMS("GlobalLandCover2009","http://cdetux2.unibe.ch/geoserver/lo/wms",{
        epsg: 900913,
        format: "image/jpeg",
        layers: "globcover_2009",
        transparent: true
    },{
        visibility: false,
        isBaseLayer: false,
        sphericalMercator: true,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
        opacity: 0.6
    }),
    new OpenLayers.Layer.WMS("GlobalCropland","http://cdetux2.unibe.ch/geoserver/lo/wms",{
        epsg: 900913,
        format: "image/jpeg",
        layers: "gl_cropland",
        transparent: true
    },{
        visibility: false,
        isBaseLayer: false,
        sphericalMercator: true,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
        opacity: 0.6
    }),
    new OpenLayers.Layer.WMS("GlobalPastureLand","http://cdetux2.unibe.ch/geoserver/lo/wms",{
        epsg: 900913,
        format: "image/jpeg",
        layers: "gl_pasture",
        transparent: true
    },{
        visibility: false,
        isBaseLayer: false,
        sphericalMercator: true,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
        opacity: 0.6
    })];

    return layers;
}