// Define the geographic and spherical mercator globally
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
                // Store the current location in a cookie
                $.cookie("_LOCATION_", center.lon + "|" + center.lat + "|" + zoom, {
                    expires: 7
                });
            /*var ext  = map.getExtent();
                activitiesLayer.protocol.read({
                    params: {
                        epsg: 900913,
                        bbox: ext.left + "," + ext.bottom + "," + ext.right + "," + ext.top,
                        limit: 500
                    },
                    url: "/activities/geojson"
                });*/
            }
        },
        projection: sphericalMercatorProjection
    });

    /**
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
    **/


    var fillOpacity = 1;

    // Calculates the radius for clustered features
    var radius = function(feature){
        if(feature.attributes.count == 1){
            return 5;
        } else {
            return Math.min(feature.attributes.count, 12) + 5;
        }
    }

    // Returns the number of clustered features, which is used to label the clusters.
    var label = function(feature){
        if(feature.attributes.count > 1){
            return feature.attributes.count;
        } else {
            return "";
        }
    }

    // Use circles for clustered features and a triangle to symbolize singe features
    var graphicName = function(feature){
        if(feature.attributes.count == 1){
            return "triangle";
        } else {
            return "circle";
        }
    }

    // Show the main tags from all taggroups in the basic-data overlay box
    var onFeatureSelected = function(event){
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
    }

    // Reset the basic-data overlay box
    var onFeatureUnselected = function(event){
        $("#deal-shortid-span").html("#");
        $("#taggroups-ul" ).empty();
        $("#taggroups-ul").html("<li><p>No deal selected.</p></li>");
    }

    // Vector layer that contains all deals whose intention of investment is agriculture
    var agricultureDealsLayer = new OpenLayers.Layer.Vector('Agriculture Deals', {
        eventListeners: {
            "featureselected": onFeatureSelected,
            "featureunselected": onFeatureUnselected
        },
        isBaseLayer: false,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
            20037508.34, 20037508.34),
        protocol: new OpenLayers.Protocol.HTTP({
            format: new OpenLayers.Format.GeoJSON({
                externalProjection: geographicProjection,
                internalProjection: sphericalMercatorProjection
            }),
            params: {
                "a__Intention of Investment__like": "Agriculture"
            },
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
                graphicName: "${graphicName}",
                fontColor: "#ffffff",
                fontSize: "9px",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                fillColor: "#006600",
                fillOpacity: fillOpacity,
                strokeColor: "#006600",
                strokeOpacity: 0.5,
                strokeWidth: 5
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius
                }
            }),
            "select": new OpenLayers.Style({
                fontColor: "#000000",
                fillColor: "#00ffff",
                strokeColor: "#00ffff"
            })
        })
    });

    // Vector layer that contains all deals whose intention of investment is forestry
    var forestryDealsLayer = new OpenLayers.Layer.Vector('Forestry Deals', {
        eventListeners: {
            "featureselected": onFeatureSelected,
            "featureunselected": onFeatureUnselected
        },
        isBaseLayer: false,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
            20037508.34, 20037508.34),
        protocol: new OpenLayers.Protocol.HTTP({
            format: new OpenLayers.Format.GeoJSON({
                externalProjection: geographicProjection,
                internalProjection: sphericalMercatorProjection
            }),
            params: {
                "a__Intention of Investment__like": "Forestry"
            },
            url: "/activities/geojson"
        }),
        sphericalMercator: true,
        strategies: [
        new OpenLayers.Strategy.Fixed(),
        new OpenLayers.Strategy.Cluster({
            distance: 30
        })
        ],
        styleMap: new OpenLayers.StyleMap({
            "default":new OpenLayers.Style({
                fillColor: "#916100",
                fillOpacity: fillOpacity,
                fontColor: "#ffffff",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#916100",
                strokeOpacity: 0.5,
                strokeWidth: 5
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius
                }
            }),
            "select": new OpenLayers.Style({
                fillColor: "#00ffff",
                fontColor: "#000000",
                strokeColor: "#00ffff"
            })
        })
    });

    // Vector layer that contains all deals whose intention of investment is mining
    var miningDealsLayer = new OpenLayers.Layer.Vector('Mining Deals', {
        eventListeners: {
            "featureselected": onFeatureSelected,
            "featureunselected": onFeatureUnselected
        },
        isBaseLayer: false,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
            20037508.34, 20037508.34),
        protocol: new OpenLayers.Protocol.HTTP({
            format: new OpenLayers.Format.GeoJSON({
                externalProjection: geographicProjection,
                internalProjection: sphericalMercatorProjection
            }),
            params: {
                "a__Intention of Investment__like": "Mining"
            },
            url: "/activities/geojson"
        }),
        sphericalMercator: true,
        strategies: [
        new OpenLayers.Strategy.Fixed(),
        new OpenLayers.Strategy.Cluster({
            distance: 30
        })
        ],
        styleMap: new OpenLayers.StyleMap({
            "default":new OpenLayers.Style({
                fillColor: "#5a5a5a",
                fillOpacity: fillOpacity,
                fontColor: "#ffffff",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#5a5a5a",
                strokeOpacity: 0.5,
                strokeWidth: 5
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius
                }
            }),
            "select": new OpenLayers.Style({
                fontColor: "#000000",
                fillColor: "#00ffff",
                strokeColor: "#00ffff"
            })
        })
    });

    // Vector layer that contains all deals whose intention of investment is tourism
    var tourismDealsLayer = new OpenLayers.Layer.Vector('Tourism Deals', {
        eventListeners: {
            "featureselected": onFeatureSelected,
            "featureunselected": onFeatureUnselected
        },
        isBaseLayer: false,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
            20037508.34, 20037508.34),
        protocol: new OpenLayers.Protocol.HTTP({
            format: new OpenLayers.Format.GeoJSON({
                externalProjection: geographicProjection,
                internalProjection: sphericalMercatorProjection
            }),
            params: {
                "a__Intention of Investment__like": "Tourism"
            },
            url: "/activities/geojson"
        }),
        sphericalMercator: true,
        strategies: [
        new OpenLayers.Strategy.Fixed(),
        new OpenLayers.Strategy.Cluster({
            distance: 30
        })
        ],
        styleMap: new OpenLayers.StyleMap({
            "default":new OpenLayers.Style({
                fillColor: "#bd0026",
                fillOpacity: fillOpacity,
                fontColor: "#ffffff",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#bd0026",
                strokeOpacity: 0.5,
                strokeWidth: 5
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius
                }
            }),
            "select": new OpenLayers.Style({
                fontColor: "#000000",
                fillColor: "#00ffff",
                strokeColor: "#00ffff"
            })
        })
    });

    // Vector layer that contains all deals with other intentions of investment
    var otherDealsLayer = new OpenLayers.Layer.Vector('Other Deals', {
        eventListeners: {
            "featureselected": onFeatureSelected,
            "featureunselected": onFeatureUnselected
        },
        isBaseLayer: false,
        maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
            20037508.34, 20037508.34),
        protocol: new OpenLayers.Protocol.HTTP({
            format: new OpenLayers.Format.GeoJSON({
                externalProjection: geographicProjection,
                internalProjection: sphericalMercatorProjection
            }),
            params: {
                "a__Intention of Investment__like": "Other"
            },
            url: "/activities/geojson"
        }),
        sphericalMercator: true,
        strategies: [
        new OpenLayers.Strategy.Fixed(),
        new OpenLayers.Strategy.Cluster({
            distance: 30
        })
        ],
        styleMap: new OpenLayers.StyleMap({
            "default":new OpenLayers.Style({
                fillColor: "#ffffff",
                fillOpacity: fillOpacity,
                fontColor: "#000000",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#ffffff",
                strokeOpacity: 0.5,
                strokeWidth: 5
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius
                }
            }),
            "select": new OpenLayers.Style({
                fillColor: "#00ffff",
                fontColor: "#000000",
                strokeColor: "#00ffff"
            })
        })
    });

    // Loop the context layers and append it to the context layers menu
    for(var i = 0; i < contextLayers.length; i++){
        var l = contextLayers[i];

        var layerName = contextLayers[i].name;

        var t = "\n\
<li>\n\
<div class=\"checkbox-modified-small\">\n\
<input class=\"input-top\" type=\"checkbox\" value=\"" + layerName + "\" id=\"checkbox" + layerName + "\">\n\
<label for=\"checkbox" + layerName + "\"></label>\n\
</div>\n\
<p class=\"context-layers-description\">" + layerName + "&nbsp;<i class=\"icon-exclamation-sign pointer\"></i>\n\
</p>\n\
</li>";
        $("#context-layers-list").append(t);
    }

    // Add the context layers to the map
    map.addLayers(contextLayers);
    // Add also the deals layers to the map
    map.addLayers([agricultureDealsLayer,
        forestryDealsLayer,
        miningDealsLayer,
        tourismDealsLayer,
        otherDealsLayer
        ]);

    // Create the SelectFeature control __after__ adding the layers to the map!
    var selectControl = new OpenLayers.Control.SelectFeature([
        agricultureDealsLayer,
        forestryDealsLayer,
        miningDealsLayer,
        tourismDealsLayer,
        otherDealsLayer
        ]);
    // Add the control to the map and activate it
    map.addControl(selectControl);
    selectControl.activate();

    // Check if a location cookie is set. If yes, center the map to this location
    var location = $.cookie("_LOCATION_");
    if(location){
        var arr = location.split("|");
        map.setCenter(new OpenLayers.LonLat(arr[0], arr[1]), arr[2]);
    }

    /**** events ****/

    // Change the base map
    $(".baseMapOptions").change(function(event){
        var bl = map.getLayersByName(event.target.value)[0];
        if(bl) {
            map.setBaseLayer(bl);
        }
    });

    // Toggle the visibility of the context layers
    $(".input-top").click(function(event){
        var ol = map.getLayersByName(event.target.value)[0];
        if(ol){
            ol.setVisibility(event.target.checked);
        }
    });

    // Collapse the filter division
    $(".filter_area_openclose > .pointer").click(function(event){
        // Do something
        //$(".filter_area").hide();
        });

    // Show the legend as overlay?
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