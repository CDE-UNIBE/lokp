/**
 * Static variables
 */
var map;

var aKeyNames, shKeyNames;

// Define the geographic and spherical mercator globally
var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");

var pointsCluster, mapInteractive, pointsVisible, contextLegendInformation,
        polygonLoadOnStart;
var mapFilterParams = [];

/**
 * Initialize the spatial search functionality.
 * Requires a text input field with id="search" and name="q".
 */
function initializeMapSearch() {
    // Add a marker layer, which is used in the location search
    var markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(markers);
    var rows = new Array();
    $("#search").typeahead({
        items: 5,
        minLength: 3,
        source: function(query, process) {
            $.get("/search", {
                q: query,
                epsg: 900913
            },
            function(response) {
                rows = new Array();
                if (response.success) {
                    for (var i = 0; i < response.data.length; i++) {
                        var row = response.data[i];
                        rows.push(row);
                    }
                }

                var results = $.map(rows, function(row) {
                    return row.name;
                });

                process(results);
            });
        },
        updater: function(item) {
            var loc = new Array();
            $.each(rows, function(row) {
                if (rows[row].name === item) {
                    loc.push(rows[row]);
                }
            });

            var selectedLocation = loc[0];
            var pos = new OpenLayers.LonLat(selectedLocation.geometry.coordinates[0], selectedLocation.geometry.coordinates[1]);

            markers.clearMarkers();
            map.setCenter(pos, 14);

            var size = new OpenLayers.Size(27, 27);
            var offset = new OpenLayers.Pixel(-(size.w / 2), -(size.h / 2));
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
 * Update the map criteria.
 * Updates the variables mapCriteria and mapValues (ajax query needed to get the
 * new values for the legend)
 *
 * Required HTML elements:
 * - <ul id="map-points-list">
 * - <div id="map-deals-symbolization">
 *
 * @param {String} translatedName
 * @param {String} internalName
 * @returns {Boolean} False
 */
function updateMapCriteria(translatedName, internalName) {

    $('#map-points-list').css('visibility', 'hidden');
    $('#map-deals-symbolization').removeClass('open').html('Loading ...');

    $.each(map.getLayersByClass("OpenLayers.Layer.Vector"), function() {
        if ($.inArray(this.name, mapValues) !== -1) {
            map.removeLayer(this);
        }
    });
    $.ajax({
        url: '/json/filtervalues',
        cache: false,
        data: {
            type: 'a',
            key: internalName
        },
        success: function(data) {
            if (data['error'])
                return;
            var newMapValues = [];
            $.each(data, function() {
                newMapValues.push(this[0]);
            });
            mapValues = newMapValues;
            mapCriteria = [translatedName, internalName, 0];
            initializeMapContent();
        }
    });
    return false;
}

/**
 * Initialize the main content (Activities) of the map with its symbolization
 * and select events.
 *
 * Necessary variables:
 * - mapValues
 * - mapCriteria
 * - allMapCriteria
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
 * HTML elements:
 * - <div id="map-point-list">
 * - <div class="deal-data">
 * - <h6 class="deal-headline"></h6>
 * - <ul id="taggroups-ul">
 * - <div id="map-deals-symbolization">
 */
function initializeMapContent() {

    // Test if the values defined in template are available
    if (typeof mapValues === 'undefined') {
        return;
    }
    if (typeof mapCriteria === 'undefined' || mapCriteria.length !== 3) {
        return;
    }
    if (typeof mapFilterParams === 'undefined') {
        filterParams = [];
    }

    if (pointsVisible !== false) {

        /**
         * Map symbolization
         * Approach: Use only one geojson request to query all the features.
         * Loop through the features and group them based on the value of the
         * map criteria. Create a layer for each group, add the correct group of
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

        // Get the data with a jQuery AJAX request. To prevent IE from caching,
        // use $.ajax instead of $.get so the parameter "cache=false" can be
        // set.
        $.ajax({
            url: '/activities/geojson?' + $.merge(['attrs=' + mapCriteria[1]], mapFilterParams).join('&'),
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
                    if (!this.attributes[mapCriteria[0]])
                        return;

                    // Make sure the mapCriteria exists in the list of available groups
                    if (!mapFeatures[this.attributes[mapCriteria[0]]])
                        return;

                    // Add it to the group
                    mapFeatures[this.attributes[mapCriteria[0]]].push(this);
                });

                // Add the symbolization dropdown and its content
                var s = [];
                s.push(
                        '<a class="dropdown-button" href="#" data-activates="map-symbolization-dropdown" style="margin: 0; padding: 0; line-height: 22px; height: 22px;">',
                        '<span id="map-symbolization-name">',
                        mapCriteria[0],
                        '</span>',
                        '<i class="material-icons right" style="line-height: 22px;">arrow_drop_down</i>',
                        '</a>',
                        '</span>',
                        '<ul id="map-symbolization-dropdown" class="dropdown-content" style="width: 500px;">'
                        );
                $.each(allMapCriteria, function() {
                    s.push(
                            '<li>',
                            '<a href="#" onclick="javascript:return updateMapCriteria(\'' + this[0].replace("'", "\\'") + '\', \'' + this[1].replace("'", "\\'") + '\');">' + this[0] + '</a>',
                            '</li>'
                            );
                });
                s.push('</ul>');
                $('#map-deals-symbolization').html(s.join(''));
                initializeDropdown();

                // Empty the legend and show it again in case it was hidden
                $("#map-points-list").empty().css('visibility', 'visible');

                // Give each group a different color
                var colorIndex = 0;

                // Loop the groups of features
                for (var l in mapFeatures) {
                    var featureLayer;

                    var styleMap = new OpenLayers.StyleMap({
                        // Get the style based on the current color
                        'default': getPointStyle(colorIndex),
                        'select': new OpenLayers.Style({
                            fontColor: '#000000',
                            fillColor: '#00ffff',
                            strokeColor: '#00ffff'
                        })
                    });

                    // Create the layer
                    if (pointsCluster === false) {
                        featureLayer = new OpenLayers.Layer.Vector(l, {
                            styleMap: styleMap
                        });
                        featureLayer.addFeatures(mapFeatures[l]);
                    } else {
                        // Create a clustering strategy for each with the
                        // features already available
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

                    if (mapInteractive !== false) {
                        featureLayer.events.on({
                            'featureselected': onFeatureSelected,
                            'featureunselected': onFeatureUnselected
                        });
                    }

                    // Do not show the layer if the points are not to be visible
                    // or if the checkbox is not checked.
                    if (pointsVisible === false ||
                        $('#activityLayerToggle').prop('checked') === false) {
                        featureLayer.setVisibility(false);
                    }

                    // Add the layer to the map and to the list of layers
                    map.addLayer(featureLayer);
                    featureLayers.push(featureLayer);

                    if (pointsCluster !== false) {
                        // If clustering is activated, do the initial clustering
                        clusterStrategy.cluster();
                    }

                    // Write a legend entry for the group
                    var legendTemplate = [
                        '<li style="line-height: 15px;">',
                        '<div class="vectorLegendSymbol" style="background-color: ' + getColor(colorIndex) + ';">',
                        '</div>',
                        l,
                        '</li>'
                    ].join('');
                    $("#map-points-list").append(legendTemplate);

                    colorIndex++;
                }

                if (mapInteractive !== false) {
                    // Create the SelectFeature control, add it for each feature
                    // layer and activate it
                    addLayersToSelectControl(map, featureLayers);
                }
            }
        });

    } else {
        $('#map-deals-symbolization').html(mapCriteria[0]);
    }

    $('#activityLayerToggle').change(function(e) {
        if (e.target.value) {
            toggleContentLayers(e.target.checked);
        }
    });

    /**
     * Functionality to select a feature on the map. Shows the details of
     * the activity (requested through service) in the detail field.
     *
     * @param {OpenLayers.Event} e Select control event.
     */
    var onFeatureSelected = function(e) {

        if (mapInteractive === false)
            return;

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
        } else if (feature.cluster.length === 1) {
            f = feature.cluster[0];
        }
        if (f) {
            var activityId = f.data.activity_identifier;
            var shortId = activityId.split("-")[0];
            $("#deal-shortid-span").html('<a href="/activities/html/' + activityId + '"># ' + shortId + '</a>');
            $("#taggroups-ul").empty().append('<li><p>' + tForLoadingdetails + '</p></li>');
            $.get("/activities/json/" + activityId, function(r) {
                var a = r.data[0];
                var tgs = a.hasOwnProperty('taggroups') ? a.taggroups : [];
                var invs = a.hasOwnProperty('involvements') ? a.involvements : [];

                $("#taggroups-ul").empty();
                $.each(tgs, function() {
                    var v;
                    if (this.main_tag && this.main_tag.key && $.inArray(this.main_tag.key, aKeyNames) > -1) {
                        v = this.main_tag.value;
                        if ($.isNumeric(v))
                            v = addCommas(v);
                        $("#taggroups-ul").append("<li><p><span class=\"bolder\">" + this.main_tag.key + ": </span>" + v + "</p></li>");
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
                    var label = (involvements.length === 1) ? tForInvestor : tForInvestors;
                    $('#taggroups-ul').append('<li class="inv"><p><span class="bolder">' + label + ': </span>' + involvements.join(', ') + '</p></li>');
                }
            });
            jQuery('html,body').animate({scrollTop: jQuery('#window_right').offset().top}, 1000);
        } else {
            $(".deal-data").empty();
            // Create a list of selected deals, when selecting several deals
            var header = $(".deal-data").append("<h5 class=\"deal-headline text-primary-color\">" + tForSelecteddeals + "</h5>");

            // Show at maximum ten deals to prevent a too long basic data box
            var maxFeatures = 5;
            if (feature.cluster.length <= maxFeatures) {
                for (var i = 0; i < feature.cluster.length; i++) {
                    var f = feature.cluster[i];
                    var activityId = f.data.activity_identifier;
                    var shortId = activityId.split("-")[0];

                    header.append("<h6><span id=\"deal-shortid-span\" class=\"underline\"><a href=\"/activities/html/" + activityId + '"># ' + shortId + '</a></span></h6>');
                }
            } else {
                for (var i = 0; i < maxFeatures; i++) {
                    var f = feature.cluster[i];
                    var activityId = f.data.activity_identifier;
                    var shortId = activityId.split("-")[0];

                    header.append("<h6><span id=\"deal-shortid-span\" class=\"underline\"><a href=\"/activities/html/" + activityId + '"># ' + shortId + '</a></span></h6>');
                }
                header.append("<span>and " + (feature.cluster.length - maxFeatures) + tForMoredeals + "</span>");
            }
        }
    };

    /**
     * Functionality to deselect a feature.
     * Resets the detail field.
     */
    var onFeatureUnselected = function() {
        if (mapInteractive === false)
            return;
        clearDetails();
    };

    /**
     * Function to add commas as a separator for thousands to a string
     * containing numbers.
     *
     * @param {String} nStr String containing numbers.
     * @returns {String} Formatted string.
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
    };
}

/**
 * Initialize the context layers of the map.
 * {showLegend}: true to display a link to show the legend
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
            '<p style="padding-top: 0; padding-bottom: 0;">',
            '<input class="input-top context-layer-checkbox" type="checkbox" value="' + layerName + '" id="checkbox' + layerName + '">',
            '<label class="text-primary-color" for="checkbox' + layerName + '">',
            layerName,
            '</label>'
        ];
        if (contextLegendInformation === true) {
            t.push(
                    '&nbsp;',
                    '<i class="icon-exclamation-sign pointer text-accent-color" onClick="javascript:showContextLegend(\'' + layerName + '\');">',
                    '</i>'
                    );
        }
        t.push(
                '</p>'
                );
        $("#context-layers-list").append(t.join(''));
    }
    // Add the context layers to the map
    map.addLayers(contextLayers);
}

/**
 * Function to initialize the polygon layers.
 * Writes the legend for the polygon layers and creates the layers if desired.
 *
 * Necessary variables:
 * - areaNames
 *
 * Required HTML elements:
 * - <ul id="map-areas-layers-list">
 */
function initializePolygonLayers() {
    for (var a in areaNames) {
        var n = areaNames[a];
        var v = n;
        if ($.isArray(n) && n.length === 2) {
            v = n[1];
            n = n[0];
        }
        var t = [
            '<p style="padding-top: 0; padding-bottom: 0;">',
            '<input class="input-top area-layer-checkbox" type="checkbox" value="' + v + '" id="checkbox' + v + '"',
        ];
        if (polygonLoadOnStart === true) {
            t.push(' checked="checked"');
        }
        t.push(
                '>',
                '<label class="text-primary-color" for="checkbox' + v + '">',
                '<span class="vectorLegendSymbolSmall" style="',
                'border: 2px solid ' + getColor(a) + ';',
                '"><span class="vectorLegendSymbolSmallInside" style="',
                'background-color: ' + getColor(a) + ';',
                'opacity: 0.5;',
                'filter: alpha(opacity=50)',
                '"></span></span>',
                n,
                '</label>',
                '</p>'
        );
        $('#map-areas-list').append(t.join(''));
        if (polygonLoadOnStart === true) {
            setPolygonLayerByName(map, v, true);
        }
    }
}

/**
 * Return the base layers of the map.
 */
function getBaseLayers() {
    var layers = [new OpenLayers.Layer.OSM("streetMap", null, {
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
    } catch (error) {
        layers.push(new OpenLayers.Layer.OSM("satelliteMap", [
            "http://oatile1.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile2.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile3.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile4.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg"
        ], {
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
 * - checkbox input fields with class="context-layer-checkbox"
 */
function initializeContextLayerControl() {
    $('.context-layer-checkbox').click(function(e) {
        if (e.target.value) {
            setContextLayerByName(map, e.target.value, e.target.checked);
        }
    });
}

/**
 * Initialize the functionality to turn polygon layers on and off.
 *
 * Required HTML elements:
 * - checkbox input fields with class="area-layer-checkbox"
 */
function initializePolygonLayerControl() {
    $('.area-layer-checkbox').click(function(e) {
        if (e.target.value) {
            setPolygonLayerByName(map, e.target.value, e.target.checked);
        }
    });
}

/**
 * Set a base layer based on its name if it exists.
 *
 * @param {OpenLayers.Map} map
 * @param {String} name
 */
function setBaseLayerByName(map, name) {
    var l = map.getLayersByName(name);
    if (l.length > 0) {
        map.setBaseLayer(l[0]);
    }
}

/**
 * Set a context layer based on its name if it exists.
 * @param {OpenLayers.Map} map
 * @param {String} name
 * @param {Boolean} checked
 */
function setContextLayerByName(map, name, checked) {
    var l = map.getLayersByName(name);
    if (l.length > 0) {
        l[0].setVisibility(checked);
    }
}

/**
 * Set a polygon layer based on its name.
 * If the layer does not yet exist, the data is queried and it is created.
 *
 * @param {OpenLayers.Map} map
 * @param {String} name
 * @param {Boolean} visible
 */
function setPolygonLayerByName(map, name, visible) {
    var l = map.getLayersByName(name);
    if (l.length > 0) {
        // The layer exists already, just toggle its visibility.
        l[0].setVisibility(visible);
    } else if (visible === true) {
        // The layer does not yet exist and needs to be created first.
        // Get the data with a jQuery AJAX request. To prevent IE from caching,
        // use $.ajax instead of $.get so the parameter "cache=false" can be
        // set.
        var colorIndex = 0;
        for (var a in areaNames) {
            var n = areaNames[a];
            if ($.isArray(n) && n.length === 2) {
                n = n[1];
            }
            if (n === name) {
                colorIndex = a;
                break;
            }
        }

        $.ajax({
            url: '/activities/geojson',
            cache: false,
            data: {
                attrs: name,
                tggeom: 'true'
            },
            success: function(data) {
                // Define a geojson format needed to read the features
                var geojsonFormat = new OpenLayers.Format.GeoJSON({
                    'internalProjection': sphericalMercatorProjection,
                    'externalProjection': geographicProjection
                });

                // Define a style
                var styleMap = new OpenLayers.StyleMap({
                    // Get the style based on the current color
                    'default': getPolygonStyle(colorIndex),
                    'select': new OpenLayers.Style({
                        fontColor: '#000000',
                        fillColor: '#80FFFF',
                        strokeColor: '#00ffff'
                    })
                });

                var featureLayer = new OpenLayers.Layer.Vector(name, {
                    styleMap: styleMap
                });
                featureLayer.addFeatures(geojsonFormat.read(data));

                if (mapInteractive !== false) {
                    featureLayer.events.on({
                        'featureselected': onFeatureSelected,
                        'featureunselected': onFeatureUnselected
                    });
                }

                // Add the layer to the map and to the list of layers
                map.addLayer(featureLayer);

                if (mapInteractive !== false) {
                    addLayersToSelectControl(map, [featureLayer]);
                }
            }
        });
    }

    /**
     * Functionality to select a feature on the map. Shows the details of the
     * polygon in the detail field.
     *
     * @param {OpenLayers.Event} e Select control event.
     */
    var onFeatureSelected = function(e) {
        if (mapInteractive === false)
            return;
        var feature = e.feature;
        if (feature) {
            var activityId = feature.data.activity_identifier;
            var shortId = activityId.split('-')[0];
            $('#deal-shortid-span').html('<a href="/activities/html/' + activityId + '"># ' + shortId + '</a>');
            $("#taggroups-ul").empty();
            $.each(feature.data, function(key, value) {
                var ignored = ['status', 'version', 'activity_identifier',
                    'status_id'];
                if ($.inArray(key, ignored) === -1) {
                    var c = [
                        '<li><p>',
                        '<span class="bolder">',
                        key,
                        ': </span>',
                        value,
                        '</p></li>'
                    ];
                    $('#taggroups-ul').append(c.join(''));
                }
            });
        }
    };

    var onFeatureUnselected = function() {
        if (mapInteractive === false)
            return;
        clearDetails();
    };
}

/**
 * Set all the content (Activity) layers to visible or not.
 *
 * @param {Boolean} visible
 */
function toggleContentLayers(visible) {

    if (pointsVisible === false) {
        // Set the layer visible for the first time. Query the layer data.
        pointsVisible = true;
        updateMapCriteria(mapCriteria[0], mapCriteria[1]);
        $('#map-points-list').show();
        $('.contentLayersMainCheckbox').css('margin-bottom', 0);
    }

    $.each(map.getLayersByClass("OpenLayers.Layer.Vector"), function() {
        if ($.inArray(this.name, mapValues) !== -1) {
            this.setVisibility(visible);
        }
    });
}

/**
 * Function to get the style of a clustered layer based on a color index.
 * Returns an OpenLayers.Style object
 *
 * @param {Integer} index
 * @returns {OpenLayers.Style}
 */
function getPointStyle(index) {

    // Define some style variables
    var fillOpacity = 1;

    var strokeOpacity = function(feature) {
        var f;
        if (feature.attributes.count === 1) {
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
        if (feature.attributes.count === 1) {
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
        if (!feature.attributes.count || feature.attributes.count === 1) {
            return 6;
        } else {
            return Math.min(feature.attributes.count, 12) + 5;
        }
    };

    // Returns the number of clustered features, which is used to label the clusters.
    var label = function(feature) {
        if (feature.attributes.count > 1) {
            return feature.attributes.count;
        } else {
            return '';
        }
    };

    // Use circles for clustered features and a triangle to symbolize singe features
    var graphicName = function(feature) {
        if (feature.attributes.count === 1 || !feature.attributes.count) {
            return 'triangle';
        } else {
            return 'circle';
        }
    };

    var fillColor = function(feature) {
        var f;
        if (feature.attributes.count === 1) {
            f = feature.cluster[0];
        } else if (!feature.attributes.count) {
            f = feature;
        }
        if (f && f.attributes.status === 'pending') {
            return '#ffffff';
        }
        return getColor(index);
    };

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
 * Create and return the style for the polygons.
 *
 * @param {Integer} index
 * @param {String} strokeColor The HTML color code of the polygon stroke
 * @returns {OpenLayers.Style}
 */
function getPolygonStyle(index, strokeColor) {

    var fillColor = function() {
        return getColor(index);
    };

    var getStrokeColor = function() {
        if (strokeColor !== undefined) {
            return strokeColor;
        }
        return getColor(index);
    };

    var style = new OpenLayers.Style({
        fillColor: '${fillColor}',
        fillOpacity: 0.5,
        strokeColor: '${strokeColor}',
        strokeOpacity: 1
    }, {
        context: {
            fillColor: fillColor,
            strokeColor: getStrokeColor
        }
    });
    return style;
}

/**
 * Function to get a color from a predefined list of available colors based on
 * an index.
 *
 * @param {type} index
 * @returns {String} A hexadecimal string representation of a color.
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
    return colors[index % colors.length];
}

/**
 * Store the current location (the extent) of the map in a cookie.
 */
function storeMapExtent() {
    $.cookie("_LOCATION_", map.getExtent().toString(), {
        expires: 7
    });
}

/**
 * Adds an array of layers to the select control of the map.
 * If the select control exists already, the new layers are added. If there is
 * no select control yet, it is created.
 *
 * @param {OpenLayers.Map} map
 * @param {arrary} layers
 */
function addLayersToSelectControl(map, layers) {
    var selectControls = map.getControlsByClass("OpenLayers.Control.SelectFeature");
    if (selectControls.length > 0) {
        // Add the layers to the existing selectable layers.
        var oldLayers = selectControls[0].layers;
        selectControls[0].setLayer(oldLayers.concat(layers));
    } else {
        // Create a new control on the layers.
        var selectControl = new OpenLayers.Control.SelectFeature(layers);
        map.addControl(selectControl);
        selectControl.activate();
    }
}

/**
 * Functionality to clear the details panel.
 */
function clearDetails() {
    $("#taggroups-ul").empty();
    $(".deal-data").empty()
            .append("<h5 class=\"deal-headline text-primary-color\">" + tForDeals + " <span id=\"deal-shortid-span\" class=\"underline\">#</span></h5>")
            .append('<ul id="taggroups-ul"><li><p>' + tForNodealselected + '</p></li></ul>');
}

/**
 * Function to toggle the chevron of an element.
 *
 * @param {Selector} el The selector of the parent element
 * @param {Integer} i Even: icon-chevron-right / Uneven: icon-chevron-down
 * @param {String} open The class of the chevron when open (default: right)
 * @param {String} close The class of the chevron when closed (default: down)
 */
function toggleChevron(el, i, open, closed) {
    open = typeof open !== 'undefined' ? open : 'right';
    closed = typeof closed !== 'undefined' ? closed : 'down';
    var oldCls = 'icon-chevron-' + open;
    var newCls = 'icon-chevron-' + closed;
    if (i % 2 === 1) {
        oldCls = 'icon-chevron-' + closed;
        newCls = 'icon-chevron-' + open;
    }
    $(el).find('.' + oldCls).removeClass(oldCls).addClass(newCls);
}
