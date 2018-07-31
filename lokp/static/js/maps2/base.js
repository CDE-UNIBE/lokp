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
 * Return an object containing base layers. The key is used as identifier of the
 * layer.
 */
function getContextLayers(mapId, layerConfigs) {
    var defaultConfig = {
        format: 'image/png',
        transparent: true,
        visible: false,
        opacity: 0.6
    };
    var layerHtml = '';
    var layers = {};
    layerConfigs.forEach(function(layerConfig) {
        layerHtml += '<p class="context-layer-checkbox-entry">' +
            '<input class="input-top context-layer-checkbox" type="checkbox" value="' + layerConfig.name + '" id="checkbox-' + mapId + '-' + layerConfig.name + '">' +
            '<label class="text-primary-color" for="checkbox-' + mapId + '-' + layerConfig.name + '">' +
            layerConfig.name +
            '</label>' +
            '&nbsp; <i class="icon-exclamation-sign pointer text-accent-color context-layer-info" data-layer="' + layerConfig.name + '"></i>' +
            '</p>';
        var config = $.extend({}, defaultConfig, {
            epsg: layerConfig.epsg,
            format: layerConfig.format,
            layers: layerConfig.layers
        });
        var layer = L.tileLayer.wms(layerConfig.url, config);
        layer.url = layerConfig.url;
        layer.abstract = layerConfig.abstract;
        layers[layerConfig.name] = layer;
    });
    $('#context-layers-list-' + mapId).html(layerHtml);
    return layers;
}


/**
 * Initialize polygon layer controls.
 */
function initPolygonLayers(mapId, polygonKeys) {
    var html = '';
    polygonKeys.forEach(function(keyPair, i) {
        var name = keyPair[0];
        var key = keyPair[1];
        var color = getColors(i)[0];
        html += '<p class="map-polygon-entry">' +
            '<input class="input-top area-layer-checkbox" type="checkbox" data-layer="' + key + '" id="map-' + mapId + '-poly-' + key + '">' +
            '<label class="text-primary-color" for="map-' + mapId + '-poly-' + key + '">' +
            '<span class="vectorLegendSymbolSmall" style="border: 2px solid ' + color + '">' +
            '<span class="vectorLegendSymbolSmallInside" style="background-color: ' + color + '; opacity: 0.5; filter: alpha(opacity=50);"></span>' +
            '</span>' +
            name +
            '</label>' +
            '</p>';
    });
    $('#map-polygons-list-' + mapId).html(html);
    $('.area-layer-checkbox').change(function(e) {
        var layerId = $(e.target).data('layer');
        if (e.target.checked) {
            // Show layer
            setPolygonLayer(getMapIdFromElement(e.target), layerId)
        } else {
            // Hide layer
            var mapOptions = getMapOptionsById(mapId);
            var layer = mapOptions.polygonLayers[layerId];
            if (typeof layer !== 'undefined') {
                mapOptions.map.removeLayer(layer);
            }
        }
    });
}


function setPolygonLayer(mapId, layerId) {
    var mapOptions = getMapOptionsById(mapId);
    if (typeof mapOptions.polygonLayers[layerId] === 'undefined') {
        // Create new layer
        $.ajax({
            url: '/activities/geojson',
            cache: false,
            data: {
                attrs: layerId,
                tggeom: 'true'
            },
            success: function(data) {
                var mapKeys = mapOptions.mapVariables.polygon_keys.map(function(k) { return k[1]; });
                var color = getColors(mapKeys.indexOf(layerId))[0];
                var layer = L.geoJSON(data, {
                    style: function(feature) {
                        return {color: color}
                    }
                });
                layer.on('click', function(a) {
                    showSingleFeatureDetails(a, mapOptions);
                });
                layer.addTo(mapOptions.map);
                mapOptions.polygonLayers[layerId] = layer;
            }
        })
    } else {
        // Layer exists already, just display it
        mapOptions.polygonLayers[layerId].addTo(mapOptions.map);
    }
}


/**
 * Initialize the radio buttons used to switch base layers.
 */
function initBaseLayerControl() {
    // Change the currently visible base map
    $('.js-base-map-layers').change(function(e) {
        if (!e.target.value) return;

        // Get current map and layers
        var mapOptions = window.lokp_maps[getMapIdFromElement(e.target)];
        var layer = mapOptions.baseLayers[e.target.value];
        if (typeof layer === 'undefined' || mapOptions.activeBaseLayer === layer) return;

        // Change layers
        mapOptions.map.removeLayer(mapOptions.activeBaseLayer);
        mapOptions.map.addLayer(layer);

        // Keep track of new active base layer
        mapOptions.activeBaseLayer = layer;
    });
}


/**
 * Initialize the checkboxes used to switch context layers, show modal with
 * legend information and transparency slider for context layers.
 */
function initContextLayerControl() {
    $('.context-layer-checkbox').change(function(e) {
        var mapOptions = window.lokp_maps[getMapIdFromElement(e.target)];
        var layer = mapOptions.contextLayers[e.target.value];
        if (this.checked) {
            mapOptions.map.addLayer(layer);
        } else {
            mapOptions.map.removeLayer(layer);
        }
    });
    $('.context-layer-info').click(function(e) {
        var mapId = getMapIdFromElement(e.target);
        var mapOptions = window.lokp_maps[mapId];
        var layerName = $(this).data('layer');
        var layer = mapOptions.contextLayers[layerName];
        showContextLegendModal(mapId, layerName, layer);
    });
    $('.layer-transparency-slider').on('input', function(e) {
        var mapOptions = window.lokp_maps[$(this).data('map-id')];
        for (var layerName in mapOptions.contextLayers) {
            if (mapOptions.contextLayers.hasOwnProperty(layerName)) {
                mapOptions.contextLayers[layerName].setOpacity(this.value / 100);
            }
        }
    });
}


/**
 * Initialize field to search for places with Google.
 */
function initMapSearch(mapId) {
    var searchField = $('#js-map-search-' + mapId);  //

    if (searchField.length === 0) return;

    var mapSearch = new google.maps.places.SearchBox(searchField[0]);
    mapSearch.addListener('places_changed', function() {
        var places = this.getPlaces();
        if (places.length !== 1) return;
        var loc = places[0].geometry.location.toJSON();
        var mapOptions = getMapOptionsById(mapId);
        var map = mapOptions.map;

        // Zoom to location
        var latLng = L.latLng(loc.lat, loc.lng);
        map.setView(latLng, 14);

        // Set marker if wanted.
        if (searchField.data('set-marker')) {
            if (mapOptions.activeMapMarker !== null) {
                map.removeLayer(mapOptions.activeMapMarker);
            }
            var marker = L.marker(latLng);
            marker.addTo(map);
            mapOptions.activeMapMarker = marker;
            // Remove marker on click.
            marker.on('click', function() {
                map.removeLayer(this);
                mapOptions.activeMapMarker = null;
            });
        }
    });
}


/**
 * Get the legend graphic and show it in a modal, along with the abstract
 * defined in the configuration yaml.
 */
function showContextLegendModal(mapId, name, layer) {
    // Prepare URL of legend image
    var imgParams = {
        request: 'GetLegendGraphic',
        service: layer.wmsParams.service,
        version: layer.wmsParams.version,
        layer: encodeURI(layer.wmsParams.layers),
        style: layer.wmsParams.styles,
        format: layer.wmsParams.format,
        width: 25,
        height: 25,
        legend_options: 'forceLabels:1;fontAntiAliasing:1;fontName:Nimbus Sans L Regular;'
    };
    var imgUrl = layer.url + '?' + decodeURI($.param(imgParams));

    $('#map-modal-body-' + mapId).html(
        '<div id="map-modal-loading-' + mapId + '" style="text-align: center;">' +
        '<img src="/custom/img/ajax-loader.gif" height="55" width="54">' +
        '</div>' +
        '<div id="map-modal-legend-content-' + mapId + '" class="hide">' +
        '<h6 class="legend-modal-title">' + name + '</h6>' +
        '<div id="legend-modal-legend-abstract-' + mapId + '"></div>' +
        '<img class="map-modal-legend-image" src="' + imgUrl + '">' +
        '</div>');

    // Show the model window
    $('#map-modal-' + mapId).openModal();

    // If an abstract is set in the YAML, use this one
    if (typeof layer.abstract !== 'undefined') {
        $('#legend-modal-legend-abstract-' + mapId).html(layer.abstract);
    }

    $('#map-modal-legend-content-' + mapId).removeClass('hide');
    $('#map-modal-loading-' + mapId).hide();
}


/**
 * Initialize the map content by querying the activities, grouping them and
 * putting them on a map.
 *
 * @param map
 */
function initMapContent(map) {

    // zoom to myanmar
    map.setView([21.9162, 95.9560], 6);

    var mapOptions = getMapOptionsFromMap(map);
    var mapCriteria = mapOptions.mapVariables.map_criteria;
    var mapValues = mapOptions.mapVariables.map_symbol_values;
    var allMapCriteria = mapOptions.mapVariables.map_criteria_all;
    var pointsCluster = mapOptions.options.pointsCluster;

    $('.js-activity-layer-toggle').on('change', function() {
        var mapOpts = getMapOptionsFromElement(this);
        if (typeof mapOpts.dealLayer === 'undefined') return;
        if (this.checked) {
            mapOpts.map.addLayer(mapOpts.dealLayer);
        } else {
            mapOpts.map.removeLayer(mapOpts.dealLayer);
        }
    });

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

                        marker.on('click', function(a) {
                            showSingleFeatureDetails(a, mapOptions);
                        });
                        marker.on('clusterclick', function(a) {
                            showClusterFeatureDetails(a, mapOptions);
                        });

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

            var mapOptions = getMapOptionsFromMap(map);
            if (mapOptions.options.pointsVisible === true) {
                map.addLayer(dealLayer);
            }
            mapOptions['dealLayer'] = dealLayer;

            // Map symbolization dropdown
            var symbolsHtml = [];
            symbolsHtml.push(
                '<a class="dropdown-button" href="#" data-activates="map-symbolization-dropdown-' + map.getContainer().id + '" style="margin: 0; padding: 0; line-height: 22px; height: 22px;">',
                    mapCriteria[0],
                    '<i class="material-icons right" style="line-height: 22px;">arrow_drop_down</i>',
                '</a>',
                '<ul id="map-symbolization-dropdown-' + map.getContainer().id + '" class="dropdown-content" style="width: 500px;">'
            );
            allMapCriteria.forEach(function(c) {
                symbolsHtml.push(
                    '<li>',
                        '<a href="#" class="js-change-map-symbolization" data-map-id="' + map.getContainer().id + '" data-translated-name="' + c[0].replace("'", "\\'") + '" data-internal-name="' + c[1].replace("'", "\\'") + '">' + c[0] + '</a>',
                    '</li>'
                )
            });
            symbolsHtml.push('</ul>');
            $('#map-deals-symbolization-' + map.getContainer().id).html(symbolsHtml.join(''));
            initializeDropdown();

            $('.js-change-map-symbolization').on('click', function(e) {
                e.preventDefault();
                var $t = $(this);
                updateMapCriteria($t.data('map-id'), $t.data('translated-name'), $t.data('internal-name'));
            });

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
            $('#map-points-list-' + map.getContainer().id).html(legendHtml.join(''));
        }
    });
}


/**
 * When selecting a single feature, show its details.
 */
function showSingleFeatureDetails(a, mapOptions) {
    if (typeof mapOptions.options.detailPanelId === 'undefined') return;
    var detailContainer = $('#' + mapOptions.options.detailPanelId);
    detailContainer.html(mapOptions.mapVariables.translations.loading);
    var feature = a.layer.feature;
    $.get('/activities/map_selection/' + feature.properties.activity_identifier, function(data) {
        detailContainer.html(data);
    });
}


/**
 * When selecting a cluster of features, show their details (limit will be set
 * by backend)
 */
function showClusterFeatureDetails(a, mapOptions) {
    if (typeof mapOptions.options.detailPanelId === 'undefined') return;
    var detailContainer = $('#' + mapOptions.options.detailPanelId);
    detailContainer.html(mapOptions.mapVariables.translations.loading);
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
            if (data['error']) return;
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
    return $(el).closest('ul').data('map-id');
}


function getMapOptionsFromElement(el) {
    return getMapOptionsById(getMapIdFromElement(el));
}


function getMapOptionsById(id) {
    return window.lokp_maps[id];
}


/**
 * Helper to get the map options from a map.
 * @param map
 */
function getMapOptionsFromMap(map) {
    return getMapOptionsById(map.getContainer().id);
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
