/**
 * Return an object containing base layers. The first entry is usually used as
 * default layer. The key is used as identifier of the layer.
 */
function getBaseLayers() {
    return {
        'satelliteMap': L.gridLayer.googleMutant({
            type: 'hybrid'
        }),
        'esriSatellite': L.tileLayer('//server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        }),
        'terrainMap': L.gridLayer.googleMutant({
            type: 'terrain'
        }),
        'streetMap': L.tileLayer('//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        })
    };
}


/**
 * Initialize the radio buttons used to switch base layers.
 */
function initBaseLayerControl() {
    // Change the currently visible base map
    $('.baseMapOptions').change(function(e) {
        if (!e.target.value) return;

        // Get current map and layers
        var mapOptions = window.lokp_maps[getMapIdFromElement(e.target)];
        var layer = mapOptions.baseLayers[e.target.value];
        if (typeof layer === 'undefined') return;

        // Change layers
        mapOptions.map.removeLayer(mapOptions.activeBaseLayer);
        mapOptions.map.addLayer(layer);

        // Keep track of new active base layer
        mapOptions.activeBaseLayer = layer;
    });
}


/**
 * Initialize the map content by querying the activities, grouping them and
 * putting them on a map.
 *
 * @param map
 */
function initMapContent(map) {

    var mapOptions = getMapOptionsFromMap(map);
    var mapCriteria = mapOptions.mapVariables.map_criteria;
    var mapValues = mapOptions.mapVariables.map_symbol_values;
    var allMapCriteria = mapOptions.mapVariables.map_criteria_all;

    if (mapOptions.options.pointsVisible === false) {
        $('#map-deals-symbolization').html('Points are not visible on this map.');
        return;
    }
    var pointsCluster = mapOptions.options.pointsCluster;

    var queryParams = $.merge(
        ['attrs=' + mapCriteria[1]], getActiveFilters()).join('&');
    $.ajax({
        url: '/activities/geojson?' + queryParams,
        cache: false,
        success: function(data) {
            var dataGrouped = {};
            data.features.forEach(function(feature) {
                var groupBy = feature.properties[mapCriteria[0]];
                if (typeof dataGrouped[groupBy] === 'undefined') {
                    dataGrouped[groupBy] = [];
                }
                dataGrouped[groupBy].push(feature);
            });

            var dealLayer = L.layerGroup();
            
            for (var key in dataGrouped) {
                if (dataGrouped.hasOwnProperty(key)) {
                    var geojson = {
                        'type': 'FeatureCollection',
                        'features': dataGrouped[key]
                    };
                    var geojsonLayer;

                    if (pointsCluster === true) {
                        // Define a cluster of markers for each map criteria value
                        var marker = L.markerClusterGroup({
                            showCoverageOnHover: false,
                            zoomToBoundsOnClick: false,
                            maxClusterRadius: 50,
                            singleMarkerMode: true,
                            // Store the current key so it can be accessed from
                            // within the iconCreateFunction.
                            options: {
                                'key': key
                            },
                            iconCreateFunction: function(cluster) {
                                // Overwrite the default icons: Always use color of
                                // the current map criteria value.
                                var colors = getColors(mapValues.indexOf(this.options.key));
                                var textColor = colors[1];
                                var iconColor = chroma(colors[0]).alpha(0.6);
                                var altIconColor = textColor === '#FFFFFF' ? iconColor.brighten(0.5) : iconColor.darken(0.5);

                                var childCount = cluster.getChildCount();
                                if (childCount === 1) {
                                    // For single features, flag if status is pending
                                    var feature = cluster.getAllChildMarkers()[0].feature;
                                    altIconColor = textColor === '#FFFFFF' ? iconColor.brighten(0.5) : iconColor.darken(0.5);
                                    if (feature.properties.status === 'pending') {
                                        altIconColor = 'white';
                                    }
                                    return L.divIcon({
                                        className: 'map-single-icon',
                                        iconSize: new L.Point(20, 20),
                                        html: '<div style="background-color: ' + altIconColor + '"><div style="background-color: ' + iconColor + '"></div></div>'
                                    });
                                }

                                return L.divIcon({
                                    html: '<div style="color: ' + textColor + '; background-color: ' +  altIconColor + '"><div style="background-color: ' + iconColor + '"><span>' + childCount + '</span></div></div>',
                                    iconSize: L.point(40, 40),
                                    className: 'map-cluster-icon'
                                });
                            }
                        });

                        geojsonLayer = L.geoJson(geojson);
                        marker.addLayer(geojsonLayer);

                        marker.on('click', showSingleFeatureDetails);
                        marker.on('clusterclick', showClusterFeatureDetails);

                        dealLayer.addLayer(marker);
                    } else {
                        // No clustering: Show each feature as point.
                        geojsonLayer = L.geoJson(geojson, {
                            pointToLayer: function(geoJsonPoint, latlng) {
                                var colors = getColors(mapValues.indexOf(key));
                                var textColor = colors[1];
                                var iconColor = chroma(colors[0]).alpha(0.6);
                                var altIconColor = textColor === '#FFFFFF' ? iconColor.brighten(0.5) : iconColor.darken(0.5);
                                if (geoJsonPoint.properties.status === 'pending') {
                                    altIconColor = 'white';
                                }
                                return L.marker(latlng, {
                                    icon: L.divIcon({
                                        className: 'map-single-icon',
                                        iconSize: new L.Point(20, 20),
                                        html: '<div style="background-color: ' + altIconColor + '"><div style="background-color: ' + iconColor + '"></div></div>'
                                    })
                                });
                            }
                        });
                        dealLayer.addLayer(geojsonLayer);
                    }
                }
            }

            map.addLayer(dealLayer);
            var mapOptions = getMapOptionsFromMap(map);
            mapOptions['dealLayer'] = dealLayer;

            // Map symbolization dropdown
            var symbolsHtml = [];
            symbolsHtml.push(
                '<a class="dropdown-button" href="#" data-activates="map-symbolization-dropdown" style="margin: 0; padding: 0; line-height: 22px; height: 22px;">',
                    '<span id="map-symbolization-name">',
                        mapCriteria[0],
                    '</span>',
                    '<i class="material-icons right" style="line-height: 22px;">arrow_drop_down</i>',
                '</a>',
                '<ul id="map-symbolization-dropdown" class="dropdown-content" style="width: 500px;">'
            );
            allMapCriteria.forEach(function(c) {
                symbolsHtml.push(
                    '<li>',
                        '<a href="#" onclick="javascript:return updateMapCriteria(\'' + map.getContainer().id + '\', \'' + c[0].replace("'", "\\'") + '\', \'' + c[1].replace("'", "\\'") + '\');">' + c[0] + '</a>',
                    '</li>'
                )
            });
            symbolsHtml.push('</ul>');
            $('#map-deals-symbolization').html(symbolsHtml.join(''));
            initializeDropdown();
            
            // Legend
            var legendHtml = mapValues.map(function(v, i) {
                return [
                    '<li style="line-height: 15px;">',
                        '<div class="vectorLegendSymbol" style="background-color: ' + getColors(i)[0] + ';">',
                        '</div>',
                        v,
                    '</li>'
                ].join('');
            });
            $('#map-points-list').html(legendHtml.join(''));
        }
    });
}


/**
 * When selecting a single feature, show its details.
 *
 * @param a
 */
function showSingleFeatureDetails(a) {
    var detailContainer = $('#tab1');
    detailContainer.html(tForLoading);
    var feature = a.layer.feature;
    $.get('/activities/map_selection/' + feature.properties.activity_identifier, function(data) {
        detailContainer.html(data);
    });
}


/**
 * When selecting a cluster of features, show their details (limit will be set
 * by backend)
 *
 * @param a
 */
function showClusterFeatureDetails(a) {
    var detailContainer = $('#tab1');
    detailContainer.html(tForLoading);
    var identifiers = a.layer.getAllChildMarkers().map(function(m) {
        return m.feature.properties.activity_identifier;
    });
    $.get('/activities/map_selection/' + identifiers.join(','), function(data) {
        detailContainer.html(data);
    });
}


/**
 * Update the criteria used for symbolization of activities.
 *
 * @param mapId
 * @param translatedName
 * @param internalName
 */
function updateMapCriteria(mapId, translatedName, internalName) {
    var mapOptions = window.lokp_maps[mapId];

    var map = mapOptions.map;

    if (typeof mapOptions.dealLayer !== 'undefined') {
        map.removeLayer(mapOptions.dealLayer);
        mapOptions.dealLayer = null;
    }

    // Query the values for the new key
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
            mapOptions.mapVariables.map_symbol_values = data.map(function(d) {
                return d[0];
            });
            mapOptions.mapVariables.map_criteria = [translatedName, internalName, -1];
            initMapContent(map);
        }
    });
}


/**
 * Helper to get the map ID from an element.
 * @param el
 */
function getMapIdFromElement(el) {
    return $(el).closest('form').data('map-id');
}


/**
 * Helper to get the map options from a map.
 * @param map
 */
function getMapOptionsFromMap(map) {
    return window.lokp_maps[map.getContainer().id];
}


/**
 * Collect any active filters (both A and SH)
 */
function getActiveFilters() {
    var activeFilters = [];
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        if (hashes[i].lastIndexOf('a__', 0) === 0 || hashes[i].lastIndexOf('sh__', 0) === 0) {
            activeFilters.push(hashes[i]);
        }
    }
    return activeFilters;
}

/**
 * Get colors by index. Returns a list of
 * - [0] icon_color
 * - [1] text_color
 *
 * @param index
 */
function getColors(index) {
    var colors = [
        ['#1d6914', '#FFFFFF'],
        ['#575757', '#FFFFFF'],
        ['#2a4bd7', '#FFFFFF'],
        ['#ad2323', '#FFFFFF'],
        ['#814a19', '#FFFFFF'],
        ['#8126c0', '#FFFFFF'],
        ['#81c57a', '#000000'],
        ['#9dafff', '#000000'],
        ['#29d0d0', '#000000'],
        ['#ff9233', '#000000'],
        ['#ffee33', '#000000'],
        ['#e9debb', '#000000'],
        ['#ffcdf3', '#000000'],
        ['#a0a0a0', '#000000']
    ];
    // Do not break if index > length
    return colors[index % colors.length];
}
