/**
 * Necessary variables with translated text for this file (must be defined and
 * translated in template):
 * tForDeals
 * tForInvestor
 * tForInvestors
 * tForLegend
 * tForLegendforcontextlayer
 * tForLoading
 * tForLoadingdetails
 * tForMoredeals
 * tForNodealselected
 * tForSelecteddeals
 * tForDealsGroupedBy
 */

/**
 * GLOBAL VARIABLES
 */
var map;

/**
 * ON START
 */
$(document).ready(function() {

    // Prepare keys to show in overview
    // For Activities, only use the first two keys of overview
    var aKeyNames = getKeyNames(aKeys).slice(0, 2);
    // For Stakeholders, only use the first key of overview
    var shKeyNames = getKeyNames(shKeys).slice(0, 1);
    var shReprString = shKeyNames[0];

    // Collect any active filters (both A and SH)
    var filterParams = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        if (hashes[i].lastIndexOf('a__', 0) === 0 || hashes[i].lastIndexOf('sh__', 0) === 0) {
            filterParams.push(hashes[i]);
        }
    }

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
    var legendCounter = 1; // Open by default
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
    map = new OpenLayers.Map("googleMapFull", {
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
            }
        },
        projection: sphericalMercatorProjection
    });

    // Show the main tags from all taggroups in the basic-data overlay box
    var onFeatureSelected = function(event){
        var feature = event.feature;
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

    // Reset the basic-data overlay box
    var onFeatureUnselected = function(event){
        $(".basic-data").empty();
        var header = $(".basic-data").append("<h6 class=\"deal-headlline\">" + tForDeals + " <span id=\"deal-shortid-span\" class=\"underline\">#</span></h6>");
        $("#taggroups-ul" ).empty();
        $(".basic-data").append('<ul id="taggroups-ul"><li><p>' + tForNodealselected + '</p></li></ul>');
    }

    // Test if the values defined in template are available
    if (typeof mapValues === 'undefined') {
        mapValues = [];
    }
    if (typeof mapCriteria === 'undefined' || mapCriteria.length != 3) {
        mapCriteria = ['', '', 1];
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
              'internalProjection': new OpenLayers.Projection("EPSG:900913"),
              'externalProjection': new OpenLayers.Projection("EPSG:4326")
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

                // Create a clustering strategy for each with the features already
                // available
                var clusterStrategy = new OpenLayers.Strategy.Cluster({
                    distance: 30,
                    threshold: 2,
                    features: mapFeatures[l]
                });

                // Create the layer
                var featureLayer = new OpenLayers.Layer.Vector(l, {
                    strategies: [
                        clusterStrategy
                    ],
                    styleMap: new OpenLayers.StyleMap({
                        // Get the style based on the current color
                        'default': getStyle(colorIndex),
                        'select': new OpenLayers.Style({
                            fontColor: '#000000',
                            fillColor: '#00ffff',
                            strokeColor: '#00ffff'
                        })
                    }),
                    eventListeners: {
                        'featureselected': onFeatureSelected,
                        'featureunselected': onFeatureUnselected
                    }
                });
                // Add the layer to the map and to the list of layers
                map.addLayer(featureLayer);
                featureLayers.push(featureLayer);

                // Do the initial clustering of the features
                clusterStrategy.cluster();

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

            // Create the SelectFeature control, add it for each feature layer and
            // activate it
            var selectControl = new OpenLayers.Control.SelectFeature(featureLayers);
            map.addControl(selectControl);
            selectControl.activate();
        }
    });

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

    // Check if a location cookie is set. If yes, center the map to this location.
    // If no cookie is set, zoom the map to the extent of the current profile
    var location = $.cookie("_LOCATION_");
    if (location) {
        var arr = location.split(',');
        if (arr.length == 4) {
            var extent = new OpenLayers.Bounds(arr);
            map.zoomToExtent(extent, true);
        }
    } else {
        var f = new OpenLayers.Format.GeoJSON();
        // Variable profilePolygon is a GeoJSON geometry
        var profileExtent = f.read(profilePolygon, "Geometry");
        if (profileExtent) {
            // Reproject the extent to spherical mercator projection and zoom the map to its extent
            map.zoomToExtent(profileExtent.transform(geographicProjection, sphericalMercatorProjection).getBounds(), true);
        } else {
            map.zoomToMaxExtent();
        }
    }

    /**** events ****/

    // Toggle the visibility of the context layers
    $(".input-top").click(function(event){
        if (event.target.value) {
            setContextLayerByName(map, event.target.value, event.target.checked);
        }
    });

    // Map search
    initializeMapSearch(map);
});

/**
 * Function to show the legend of a context layer in a modal window.
 */
function showContextLegend(layerName) {

    // Find the layer in the list of available context layers
    var layer = null;
    $.each(contextLayers, function() {
        if (this.name == layerName) {
            layer = this;
        }
    });
    if (layer === null) return false;

    // Prepare URL of legend image
    var imgParams = {
        request: 'GetLegendGraphic',
        service: layer.params.SERVICE,
        version: layer.params.VERSION,
        layer: layer.params.LAYERS,
        style: layer.params.STYLES,
        format: 'image/png',
        width: 25,
        height: 25,
        legend_options: 'forceLabels:1;fontAntiAliasing:1;fontName:Nimbus Sans L Regular;'
    };
    var imgUrl = layer.url + '?' + $.param(imgParams);

    // Set the content: Image is hidden first while loading indicator is shown
    $('#mapModalHeader').html(tForLegend);
    $('#mapModalBody').html('<div id="contextLegendImgLoading" style="text-align: center;"><img src="/static/img/ajax-loader-green.gif" alt="' + tForLoading + '" height="55" width="54"></div><div id="contextLegendContent" class="hide"><p>' + tForLegendforcontextlayer + ' <strong>' + layerName + '</strong>:</p><img id="contextLegendImg" src="' + imgUrl + '"></div>');

    // Show the model window
    $('#mapModal').modal();

    // Once the image is loaded, hide the loading indicator and show the image
    /*$('#contextLegendImg').load(function() {
        $('#contextLegendContent').removeClass('hide');
        $('#contextLegendImgLoading').hide();
    });*/

    var getCapabilitiesRequest = layer.url + '?' + $.param({
        request: 'GetCapabilities',
        namespace: 'lo'
    });
    $.get("/proxy", {
        url: getCapabilitiesRequest
    },
    function(data){
        var xmlDoc = $.parseXML(data);
        $xml = $( xmlDoc );
        $xml.find("Layer[queryable='1']").each(function(){
            $layer = $( this );
            if($layer.find("Name").first().text() == layer.params.LAYERS || $layer.find("Name").first().text() == layer.params.LAYERS.split(":")[1]){
                var layerAbstract = $layer.find("Abstract").first().text();
                $("<p>" + layerAbstract + "</p>").insertAfter('#contextLegendContent > p');
                // Assuming to load and parse the GetCapabilites documents takes
                // longer than the image, the "Loading ..." text is hidden and the
                // #contextLegendContent div is shown as soon as the Ajax request
                // has successfully finished.
                $('#contextLegendContent').removeClass('hide');
                $('#contextLegendImgLoading').hide();
                return false;
            }
        });
    });
    return false;
}

/**
 * Function to add commas as a separator for thousands to a string containing
 * numbers.
 * Returns a formatted string.
 */
function addCommas(nStr) {
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
