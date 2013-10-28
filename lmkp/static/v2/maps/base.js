/**
 * Static variables
 */
var map;

var aKeyNames, shKeyNames;

// Define the geographic and spherical mercator globally
var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");

/**
 * Initialize the spatial search functionality.
 * Requires a text input field with id="search" and name="q".
 */
function initializeMapSearch() {
    // Add a marker layer, which is used in the location search
    var markers = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markers);
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
                markers.removeMarker(m);
            });
            markers.addMarker(m);

            return loc[0].name;
        }
    }).click(function() {
        $(this).select();
    });
}

/**
 * Initialize the main content (Activities) of the map with its symbolization
 * and select events.
 *
 * Necessary variables:
 * - mapValues
 * - mapCriteria
 *
 * Options:
 * - [boolean] cluster
 * - [boolean] interactive (*)
 *
 * (*) Option "interactive" is true:
 * Necessary variables:
 * - aKeys
 * - shKeys
 * - tForLoadingdetails
 * - tForInvestor
 * - tForInvestors
 * - tForSelecteddeals
 * - tForMoredeals
 * - tForDeals
 * - tForNodealselected
 * - tForDealsGroupedBy
 * HTML elements:
 * - <div id="map-legend-list">
 * - <div class="basic-data">
 * - <h6 class="deal-headline"></h6>
 * - <ul id="taggroups-ul">
 */
function initializeMapContent(cluster, interactive, visible) {

    // Test if the values defined in template are available
    if (typeof mapValues === 'undefined') {
        return;
    }
    if (typeof mapCriteria === 'undefined' || mapCriteria.length != 3) {
        return;
    }

    /**
     * Map symbolization
     * Approach: Use only one geojson request to query all the features. Loop
     * through the features and group them based on the value of the map
     * criteria. Create a layer for each group, add the correct group of
     * features to it and add the layer to the map.
     */

    // Prepare to collect all the features based on the map criteria
    var mapFeatures = {};
    for (var v in mapValues) {
        mapFeatures[mapValues[v]] = [];
    }

    // Also collect all the created layers in an array (needed to make them
    // selectable after adding them to the map)
    var featureLayers = [];

    // Get the data with a jQuery AJAX request. To prevent IE from caching, use
    // $.ajax instead of $.get so the parameter "cache=false" can be set.
    $.ajax({
        url: '/activities/geojson?attrs=' + mapCriteria[1],
        cache: false,
        success: function(data) {
            // Define a geojson format needed to read the features
            var geojsonFormat = new OpenLayers.Format.GeoJSON({
              'internalProjection': sphericalMercatorProjection,
              'externalProjection': geographicProjection
            });

            // Read and loop all the features, add them to the correct group
            var features = geojsonFormat.read(data);
            $.each(features, function() {

                // Make sure the mapCriteria is present in the feature
                if (!this.attributes[mapCriteria[1]]) return;

                // Make sure the mapCriteria exists in the list of available groups
                if (!mapFeatures[this.attributes[mapCriteria[1]]]) return;

                // Add it to the group
                mapFeatures[this.attributes[mapCriteria[1]]].push(this);
            });

            var legendExplanation = [
                '<div class="legendExplanation">',
                tForDealsGroupedBy, ': ',
                '<strong>', mapCriteria[0], '</strong>',
                '</div>'
            ].join('');
            $("#map-legend-list").append(legendExplanation);

            // Give each group a different color
            var colorIndex = 0;

            // Loop the groups of features
            for (var l in mapFeatures) {
                var featureLayer;

                var styleMap = new OpenLayers.StyleMap({
                    // Get the style based on the current color
                    'default': getStyle(colorIndex),
                    'select': new OpenLayers.Style({
                        fontColor: '#000000',
                        fillColor: '#00ffff',
                        strokeColor: '#00ffff'
                    })
                });

                // Create the layer
                if (cluster === false) {
                    featureLayer = new OpenLayers.Layer.Vector(l, {
                        styleMap: styleMap
                    });
                    featureLayer.addFeatures(mapFeatures[l]);
                } else {
                    // Create a clustering strategy for each with the features
                    // already available
                    var clusterStrategy = new OpenLayers.Strategy.Cluster({
                        distance: 30,
                        threshold: 2,
                        features: mapFeatures[l]
                    });
                    featureLayer = new OpenLayers.Layer.Vector(l, {
                        strategies: [
                            clusterStrategy
                        ],
                        styleMap: styleMap
                    });
                }

                if (interactive !== false) {
                    featureLayer.events.on({
                        'featureselected': onFeatureSelected,
                        'featureunselected': onFeatureUnselected
                    });
                }

                if (visible === false) {
                    featureLayer.setVisibility(false);
                }

                // Add the layer to the map and to the list of layers
                map.addLayer(featureLayer);
                featureLayers.push(featureLayer);

                if (cluster !== false) {
                    // If clustering is activated, do the initial clustering
                    clusterStrategy.cluster();
                }

                // Write a legend entry for the group
                var legendTemplate = [
                    '<li class="legendEntry">',
                    '<div class="vectorLegendSymbol" style="background-color: ' + getColor(colorIndex) + ';">',
                    '</div>',
                    l,
                    '</li>'
                ].join('');
                $("#map-legend-list").append(legendTemplate);

                colorIndex++;
            }

            if (interactive !== false) {
                // Create the SelectFeature control, add it for each feature layer and
                // activate it
                var selectControl = new OpenLayers.Control.SelectFeature(featureLayers);
                map.addControl(selectControl);
                selectControl.activate();
            }
        }
    });

    /**
     * Functionality to select a feature on the map. Shows the details of
     * the activity in the detail field.
     */
    var onFeatureSelected = function(e) {

        if (interactive === false) return;

        if (typeof aKeys === 'undefined') {
            return;
        }
        if (typeof shKeys === 'undefined') {
            return;
        }

        // For Activities, only use the first two keys of overview
        aKeyNames = getKeyNames(aKeys).slice(0, 2);
        // For Stakeholders, only use the first key of overview
        shKeyNames = getKeyNames(shKeys).slice(0, 1);
        var shReprString = shKeyNames[0];

        var feature = e.feature;
        var f;
        if (!feature.cluster) {
            f = feature;
        } else if (feature.cluster.length == 1) {
            f = feature.cluster[0];
        }
        if (f) {
            var activityId = f.data.activity_identifier;
            var shortId = activityId.split("-")[0]
            $("#deal-shortid-span").html('<a href="/activities/html/' + activityId + '"># ' + shortId + '</a>');
            $("#taggroups-ul" ).empty().append('<li><p>' + tForLoadingdetails + '</p></li>');
            $.get("/activities/json/" + activityId, function(r){
                var a = r.data[0];
                var tgs = a.hasOwnProperty('taggroups') ? a.taggroups : [];
                var invs = a.hasOwnProperty('involvements') ? a.involvements : [];

                $("#taggroups-ul" ).empty();
                $.each(tgs, function() {
                    var v;
                    if (this.main_tag && this.main_tag.key && $.inArray(this.main_tag.key, aKeyNames) > -1) {
                        v = this.main_tag.value;
                        if ($.isNumeric(v)) v = addCommas(v);
                        $( "#taggroups-ul" ).append( "<li><p><span class=\"bolder\">" + this.main_tag.key + ": </span>" + v + "</p></li>" );
                    }
                });

                var involvements = [];
                $.each(invs, function() {
                    var sh = this.data;
                    var sh_tgs = sh.hasOwnProperty('taggroups') ? sh.taggroups : [];

                    if (shReprString !== null) {
                        var s = shReprString;
                        $.each(sh_tgs, function() {
                            if (this.main_tag && this.main_tag.key && $.inArray(this.main_tag.key, shKeyNames) > -1) {
                                s = s.replace(this.main_tag.key, this.main_tag.value);
                            }
                        });
                        involvements.push(s);
                    } else {
                        $.each(sh_tgs, function() {
                            if (this.main_tag && this.main_tag.key && $.inArray(this.main_tag.key, shKeyNames) > -1) {
                                $('.inv').append('<div><span class="bolder">' + this.main_tag.key + ': </span>' + this.main_tag.value + '</div>');
                            }
                        });
                    }
                });
                if (involvements.length > 0) {
                    var label = (involvements.length == 1) ? tForInvestor : tForInvestors;
                    $('#taggroups-ul').append('<li class="inv"><p><span class="bolder">' + label + ': </span>' + involvements.join(', ') + '</p></li>')
                }
            });
        } else {
            $(".basic-data").empty();
            // Create a list of selected deals, when selecting several deals
            var header = $(".basic-data").append("<h6 class=\"deal-headline\">" + tForSelecteddeals + "</h6>");

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
                header.append("<span>and " + (feature.cluster.length - maxFeatures) + tForMoredeals + "</span>");
            }
        }
    }

    /**
     * Functionality to deselect a feature. Resets the detail field.
     */
    var onFeatureUnselected = function() {
        if (interactive === false) return;
        $("#taggroups-ul").empty();
        $(".basic-data").empty()
            .append("<h6 class=\"deal-headline\">" + tForDeals + " <span id=\"deal-shortid-span\" class=\"underline\">#</span></h6>")
            .append('<ul id="taggroups-ul"><li><p>' + tForNodealselected + '</p></li></ul>');
    }

    /**
     * Function to add commas as a separator for thousands to a string containing
     * numbers.
     * Returns a formatted string.
     */
    var addCommas = function(nStr) {
        nStr += '';
        var x = nStr.split('.');
        var x1 = x[0];
        var x2 = x.length > 1 ? '.' + x[1] : '';
        var rgx = /(\d+)(\d{3})/;
        while (rgx.test(x1)) {
            x1 = x1.replace(rgx, '$1' + ',' + '$2');
        }
        return x1 + x2;
    }
}

/**
 * Initialize the context layers of the map.
 *
 * Necessary variables:
 * - contextLayers
 *
 * Required HTML elements:
 * - <ul id="context-layers-list">
 */
function initializeContextLayers() {
    // Loop the context layers and append it to the context layers menu
    for (var c in contextLayers) {
        var layerName = contextLayers[c].name;
        var t = [
            '<li>',
            '<div class="checkbox-modified-small">',
            '<input class="input-top" type="checkbox" value="' + layerName + '" id="checkbox' + layerName + '">',
            '<label for="checkbox' + layerName + '"></label>',
            '</div>',
            '<p class="context-layers-description">',
            layerName + '&nbsp;',
            '<i class="icon-exclamation-sign pointer" onClick="javascript:showContextLegend(\'' + layerName + '\');">',
            '</i>',
            '</p>',
            '</li>'
        ].join('');
        $("#context-layers-list").append(t);
    }
    // Add the context layers to the map
    map.addLayers(contextLayers);
}

/**
 * Return the base layers of the map.
 */
function getBaseLayers() {
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

/**
 * Initialize the functionality to switch the base layer of the map.
 *
 * Required HTML elements:
 * - radio input fields with class="baseMapOptions"
 */
function initializeBaseLayerControl() {
    // Change the base map
    $('.baseMapOptions').change(function(e) {
        if (e.target.value) {
            setBaseLayerByName(map, e.target.value);
        }
    });
}

/**
 * Initialize the functionality to turn context layers on and off.
 *
 * Required HTML elements:
 * - checkbox input fields with class="input-top"
 */
function initializeContextLayerControl() {
    $(".input-top").click(function(event){
        if (event.target.value) {
            setContextLayerByName(map, event.target.value, event.target.checked);
        }
    });
}

/**
 * Set a base layer based on its name if it exists.
 */
function setBaseLayerByName(map, name) {
    var l = map.getLayersByName(name);
    if (l.length > 0) {
        map.setBaseLayer(l[0]);
    }
}

/**
 * Set a context layer based on its name if it exists.
 */
function setContextLayerByName(map, name, checked) {
    var l = map.getLayersByName(name);
    if (l.length > 0) {
        l[0].setVisibility(checked);
    }
}

/**
 * Set all the content (Activity) layers to visible or not.
 */
function toggleContentLayers(visible) {
    $.each(map.getLayersByClass("OpenLayers.Layer.Vector"), function() {
        var nonContentLayers = ['RemovePoints', 'Geometry'];
        if ($.inArray(this.name, nonContentLayers) == -1) {
            this.setVisibility(visible);
        }
    });
}

/**
 * Function to get the style of a clustered layer based on a color index.
 * Returns an OpenLayers.Style object
 */
function getStyle(index) {

    // Define some style variables
    var fillOpacity = 1;

    var strokeOpacity = function(feature){
        var f;
        if (feature.attributes.count == 1) {
            f = feature.cluster[0];
        } else if (!feature.attributes.count) {
            f = feature;
        }
        if (f && f.attributes.status === 'pending') {
            return 1;
        }
        return 0.5;
    };

    var strokeWidth = function(feature) {
        var f;
        if (feature.attributes.count == 1) {
            f = feature.cluster[0];
        } else if (!feature.attributes.count) {
            f = feature;
        }
        if (f && f.attributes.status === 'pending') {
            return 2;
        }
        return 5;
    };

    // Calculates the radius for clustered features
    var radius = function(feature) {
        if (!feature.attributes.count || feature.attributes.count == 1) {
            return 6;
        } else {
            return Math.min(feature.attributes.count, 12) + 5;
        }
    }

    // Returns the number of clustered features, which is used to label the clusters.
    var label = function(feature) {
        if (feature.attributes.count > 1) {
            return feature.attributes.count;
        } else {
            return '';
        }
    }

    // Use circles for clustered features and a triangle to symbolize singe features
    var graphicName = function(feature) {
        if (feature.attributes.count === 1 || !feature.attributes.count) {
            return 'triangle';
        } else {
            return 'circle';
        }
    }

    var fillColor = function(feature) {
        var f;
        if (feature.attributes.count == 1) {
            f = feature.cluster[0];
        } else if (!feature.attributes.count) {
            f = feature;
        }
        if (f && f.attributes.status == 'pending') {
            return '#ffffff';
        }
        return getColor(index);
    }

    var style = new OpenLayers.Style(
        {
            graphicName: '${graphicName}',
            fontColor: '#ffffff',
            fontSize: '9px',
            label: '${label}',
            pointRadius: '${radius}',
            rotation: 180.0,
            fillColor: '${fillColor}',
            fillOpacity: fillOpacity,
            strokeColor: getColor(index),
            strokeOpacity: '${strokeOpacity}',
            strokeWidth: '${strokeWidth}'
        }, {
            context: {
                graphicName: graphicName,
                label: label,
                radius: radius,
                strokeOpacity: strokeOpacity,
                strokeWidth: strokeWidth,
                fillColor: fillColor
            }
        });
    return style;
}

/**
 * Function to get a color from a predefined list of available colors based on
 * an index.
 * Returns a hexadecimal string representation of a color.
 */
function getColor(index) {
    var colors = [
        '#1d6914',
        '#575757',
        '#2a4bd7',
        '#ad2323',
        '#814a19',
        '#8126c0',
        '#81c57a',
        '#9dafff',
        '#29d0d0',
        '#ff9233',
        '#ffee33',
        '#e9debb',
        '#ffcdf3',
        '#a0a0a0'
    ];
    return colors[index%colors.length];
}

/**
 * Store the current location (the extent) of the map in a cookie.
 */
function storeMapExtent() {
    $.cookie("_LOCATION_", map.getExtent().toString(), {
        expires: 7
    });
}
