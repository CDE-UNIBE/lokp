$(document).ready(function() {

    // Collect any active filters (both A and SH)
    var filterParams = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        if (hashes[i].lastIndexOf('a__', 0) === 0 || hashes[i].lastIndexOf('sh__', 0) === 0) {
            filterParams.push(hashes[i]);
        }
    }

    /**
     * Static variables
     */
    // Define the geographic and spherical mercator globally
    var geographicProjection = new OpenLayers.Projection("EPSG:4326");
    var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");

    /**
     * Layer Legend
     */

    // Base-layers up/down
    $('.base-layers').click(function() {
        $('.base-layers-content').slideToggle();
    });

    // Context-layers up/down
    $('.context-layers').click(function() {
        $('.context-layers-content').slideToggle();
    });

    // Map legend up/down
    var legendCounter = 0;
    $('.map-legend').click(function() {
        legendCounter++;
        $('.map-legend-content').slideToggle(function() {
            if (legendCounter % 2 == 0) {
                $('.map-legend').css('margin-bottom', '15px');
            } else {
                $('.map-legend').css('margin-bottom', '5px');
            }
        });
    });

    /**
     * Map and layers
     */
    var layers = getBaseLayers();
    var map = new OpenLayers.Map("googleMapFull", {
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
                var extent = map.getExtent();
                // Store the current location (the extent) in a cookie
                $.cookie("_LOCATION_", extent.toString(), {
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
   
    var strokeOpacity = function(feature){
        if(feature.attributes.count == 1){
            var f = feature.cluster[0];
            if(f.attributes.status == "pending"){
                return 1;
            }
        }
        return 0.5;
    };

    var strokeWidth = function(feature){
        if(feature.attributes.count == 1){
            var f = feature.cluster[0];
            if(f.attributes.status == "pending"){
                return 2;
            }
        }
        return 5;
    };

    // Calculates the radius for clustered features
    var radius = function(feature){
        if(feature.attributes.count == 1){
            return 6;
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
            $(".basic-data").empty();
            // Create a list of selected deals, when selecting several deals
            var header = $(".basic-data").append("<h6 class=\"deal-headlline\">Selected Deals</h6>");

            // Show at maximum ten deals to prevent a too long basic data box
            var maxFeatures = 10;
            if(feature.cluster.length <= maxFeatures){
                for(var i = 0; i < feature.cluster.length; i++){
                    var f = feature.cluster[i];
                    var activityId = f.data.activity_identifier;
                    var shortId = activityId.split("-")[0]

                    header.append("<h6><span id=\"deal-shortid-span\" class=\"underline\"><a href=\"/activities/html/" + activityId + '"># ' + shortId + '</a></span></h6>');
                }
            } else {
                for(var i = 0; i < maxFeatures; i++){
                    var f = feature.cluster[i];
                    var activityId = f.data.activity_identifier;
                    var shortId = activityId.split("-")[0]

                    header.append("<h6><span id=\"deal-shortid-span\" class=\"underline\"><a href=\"/activities/html/" + activityId + '"># ' + shortId + '</a></span></h6>');
                }
                header.append("<span>and " + (feature.cluster.length - maxFeatures) + " more deals ...</span>");
            }

            
            
        /*
            $("#deal-shortid-span").html('# ');
            $("#taggroups-ul").empty();
            $("#taggroups-ul").append("<li><p><span class=\"bolder\">" + feature.cluster.length + " deals selected:</span> Please zoom in to get details about a single deal.</p></li>" );
            */
        }
    }

    // Reset the basic-data overlay box
    var onFeatureUnselected = function(event){
        $(".basic-data").empty();
        var header = $(".basic-data").append("<h6 class=\"deal-headlline\">Deal <span id=\"deal-shortid-span\" class=\"underline\">#</span></h6>");
        $("#taggroups-ul" ).empty();
        $(".basic-data").append('<ul id="taggroups-ul"><li><p>No deal selected.</p></li></ul>');
    }

    // Vector layer that contains all deals whose intention of investment is agriculture
    var agricultureDealsLayer = new OpenLayers.Layer.Vector('Agricultural deals', {
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
            url: "/activities/geojson?" + $.merge(["a__Intention of Investment__like=Agriculture"], filterParams).join('&')
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
                fillColor: "${fillColor}",
                fillOpacity: fillOpacity,
                strokeColor: "#006600",
                strokeOpacity: "${strokeOpacity}",
                strokeWidth: "${strokeWidth}"
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius,
                    strokeOpacity: strokeOpacity,
                    strokeWidth: strokeWidth,
                    fillColor: function(feature){
                        if(feature.attributes.count == 1){
                            var f = feature.cluster[0];
                            if(f.attributes.status == "pending"){
                                return "#ffffff";
                            }
                        }
                        return "#006600";
                    }
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
    var forestryDealsLayer = new OpenLayers.Layer.Vector('Forestry deals', {
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
            url: "/activities/geojson?" + $.merge(["a__Intention of Investment__like=Forestry"], filterParams).join('&')
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
                fillColor: "${fillColor}",
                fillOpacity: fillOpacity,
                fontColor: "#ffffff",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#916100",
                strokeOpacity: "${strokeOpacity}",
                strokeWidth: "${strokeWidth}"
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius,
                    strokeOpacity: strokeOpacity,
                    strokeWidth: strokeWidth,
                    fillColor: function(feature){
                        if(feature.attributes.count == 1){
                            var f = feature.cluster[0];
                            if(f.attributes.status == "pending"){
                                return "#ffffff";
                            }
                        }
                        return "#916100";
                    }
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
    var miningDealsLayer = new OpenLayers.Layer.Vector('Mining deals', {
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
            url: "/activities/geojson?" + $.merge(["a__Intention of Investment__like=Mining"], filterParams).join('&')
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
                fillColor: "${fillColor}",
                fillOpacity: fillOpacity,
                fontColor: "#ffffff",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#5a5a5a",
                strokeOpacity: "${strokeOpacity}",
                strokeWidth: "${strokeWidth}"
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius,
                    strokeOpacity: strokeOpacity,
                    strokeWidth: strokeWidth,
                    fillColor: function(feature){
                        if(feature.attributes.count == 1){
                            var f = feature.cluster[0];
                            if(f.attributes.status == "pending"){
                                return "#ffffff";
                            }
                        }
                        return "#5a5a5a";
                    }
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
    var tourismDealsLayer = new OpenLayers.Layer.Vector('Tourism deals', {
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
            url: "/activities/geojson?" + $.merge(["a__Intention of Investment__like=Tourism"], filterParams).join('&')
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
                fillColor: "${fillColor}",
                fillOpacity: fillOpacity,
                fontColor: "#ffffff",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#bd0026",
                strokeOpacity: "${strokeOpacity}",
                strokeWidth: "${strokeWidth}"
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius,
                    strokeOpacity: strokeOpacity,
                    strokeWidth: strokeWidth,
                    fillColor: function(feature){
                        if(feature.attributes.count == 1){
                            var f = feature.cluster[0];
                            if(f.attributes.status == "pending"){
                                return "#ffffff";
                            }
                        }
                        return "#bd0026";
                    }
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
    var otherDealsLayer = new OpenLayers.Layer.Vector('Other deals', {
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
            url: "/activities/geojson?" + $.merge(["a__Intention of Investment__like=Other"], filterParams).join('&')
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
                fillColor: "${fillColor}",
                fillOpacity: fillOpacity,
                fontColor: "#ffffff",
                fontSize: "9px",
                graphicName: "${graphicName}",
                label: "${label}",
                pointRadius: "${radius}",
                rotation: 180.0,
                strokeColor: "#04089B",
                strokeOpacity: "${strokeOpacity}",
                strokeWidth: "${strokeWidth}"
            }, {
                context: {
                    graphicName: graphicName,
                    label: label,
                    radius: radius,
                    strokeOpacity: strokeOpacity,
                    strokeWidth: strokeWidth,
                    fillColor: function(feature){
                        if(feature.attributes.count == 1){
                            var f = feature.cluster[0];
                            if(f.attributes.status == "pending"){
                                return "#ffffff";
                            }
                        }
                        return "#04089B";
                    }
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
    var vectorLayers = [agricultureDealsLayer,
    forestryDealsLayer,
    miningDealsLayer,
    tourismDealsLayer,
    otherDealsLayer
    ];
    map.addLayers(vectorLayers);

    for(var i = 0; i < vectorLayers.length; i++){
        var l = vectorLayers[i];

        var color = l.options.styleMap.styles.default.defaultStyle.strokeColor;

        var legendTemplate = "<li class=\"legendEntry\"><div class=\"vectorLegendSymbol\" style=\"background-color: " + color + ";\"></div>" + l.name + "</li>";

        $("#map-legend-list").append(legendTemplate);
    }

    // Add a marker layer, which is used in the location search
    var markers = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markers);

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

    // Check if a location cookie is set. If yes, center the map to this location.
    // If no cookie is set, zoom the map to the extent of the current profile
    var location = $.cookie("_LOCATION_");
    if (location) {
        var arr = location.split(',');
        if (arr.length == 4) {
            var extent = new OpenLayers.Bounds(arr);
            map.zoomToExtent(extent);
        }
    } else {
        var f = new OpenLayers.Format.GeoJSON();
        // Variable profilePolygon is a GeoJSON geometry
        var profileExtent = f.read(profilePolygon, "Geometry");
        // Reproject the extent to spherical mercator projection and zoom the map to its extent
        map.zoomToExtent(profileExtent.transform(geographicProjection, sphericalMercatorProjection).getBounds());
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

    var rows = new Array();

    $("#search").typeahead({
        items: 5,
        minLength: 3,
        source: function( query , process ) {
            $.get("/search", {
                q: query,
                epsg: 900913
            },
            function(response) {
                rows = new Array();
                if(response.success){
                    for(var i = 0; i < response.data.length; i++){
                        var row = response.data[i];
                        rows.push(row);
                    }
                }

                var results = $.map(rows, function(row) {
                    return row.name;
                });

                process(results);
            } );
        },
        updater: function(item){
            var loc = new Array();
            $.each(rows, function(row){
                if(rows[row].name == item){
                    loc.push(rows[row])
                }
            });
            
            var selectedLocation = loc[0];
            var pos = new OpenLayers.LonLat(selectedLocation.geometry.coordinates[0], selectedLocation.geometry.coordinates[1]);

            markers.clearMarkers();
            map.setCenter(pos, 14);

            var size = new OpenLayers.Size(27,27);
            var offset = new OpenLayers.Pixel(-(size.w/2), -(size.h/2));
            var icon = new OpenLayers.Icon('/static/img/glyphicons_185_screenshot.png', size, offset);
            var m = new OpenLayers.Marker(pos, icon);
            m.events.register('click', m, function(event) {
                console.log("event");
            });
            markers.addMarker(m);
            
            return loc[0].name;
        }
    });


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
});