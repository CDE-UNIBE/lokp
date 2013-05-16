Ext.define('Lmkp.controller.editor.Map', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
    }, {
        ref: 'mapPanelToolbar',
        selector: 'lo_publicmappanel toolbar[itemId=mapPanelToolbar]'
    }],

    init: function() {
        this.control({
            'button[itemId=mapPopupContinueButton]': {
                click: this.onMapPopupContinueButtonClick
            }
        });
    },

    onMapPopupContinueButtonClick: function() {
        var newActivityController = this.getController('activities.NewActivity');
        newActivityController.showNewActivityWindow();
    },

    /**
     * Activate the map control to create a new point on the map.
     */
    clickAddLocationButton: function() {
        var mappanel = this.getMapPanel();
        var map = mappanel.getMap();
        var controls = map.getControlsBy('type', 'createPointControl');
        if (controls && controls[0]) {
            var createPointControl = controls[0];
            createPointControl.activate();
        }
    },

    /**
     * Show a window where the user can enter coordinates. If the coordinates
     * can be parsed, a point will be put on the map.
     */
    showCoordinatesWindow: function() {
        var me = this;
        var win = Ext.create('Ext.window.Window', {
            title: Lmkp.ts.msg('mappoints_coordinates-title'),
            layout: 'fit',
            width: 400,
            items: [
                {
                    xtype: 'form',
                    border: 0,
                    bodyPadding: 5,
                    layout: 'anchor',
                    defaults: {
                        anchor: '100%'
                    },
                    items: [
                        {
                            xtype: 'fieldcontainer',
                            fieldLabel: Lmkp.ts.msg('mappoints_coordinates-format'),
                            defaultType: 'radiofield',
                            layout: 'vbox',
                            items: [
                                {
                                    boxLabel: '46&deg; 57.1578 N 7&deg; 26.1102 E',
                                    name: 'format',
                                    inputValue: 1,
                                    checked: true
                                }, {
                                    boxLabel: '46&deg; 57\' 9.468" N 7&deg; 26\' 6.612" E',
                                    name: 'format',
                                    inputValue: 2
                                }, {
                                    boxLabel: 'N 46&deg; 57.1578 E 7&deg; 26.1102',
                                    name: 'format',
                                    inputValue: 3
                                }, {
                                    boxLabel: 'N 46&deg; 57\' 9.468" E 7&deg; 26\' 6.612"',
                                    name: 'format',
                                    inputValue: 4
                                }, {
                                    boxLabel: '46.95263, 7.43517',
                                    name: 'format',
                                    inputValue: 5
                                }
                            ]
                        }, {
                            xtype: 'textfield',
                            name: 'coordinates',
                            itemId: 'coordinates',
                            allowBlank: false
                        }, {
                            xtype: 'panel',
                            itemId: 'coordinatesError',
                            html: Lmkp.ts.msg('mappoints_coordinates-parse-error'),
                            border: 0,
                            bodyPadding: 5,
                            bodyCls: 'notice',
                            hidden: true
                        }
                    ],
                    buttons: [
                        {
                            text: Lmkp.ts.msg('mappoints_set-point'),
                            formBind: true,
                            disabled: true,
                            handler: function() {
                                var form = this.up('form').getForm();
                                if (form.isValid()) {
                                    var values = form.getValues();

                                    var pattern, matches;
                                    var latsign, longsign, d1, m1, s1, d2, m2, s2;
                                    var latitude, longitude;
                                    var lonlat;

                                    // Regex inspiration by:
                                    // http://www.nearby.org.uk/tests/geotools2.js

                                    // It seems to be necessary to escape the
                                    // values. Otherwise, the degree symbol (°)
                                    // is not recognized.
                                    var str = escape(values.coordinates);
                                    // However, we do need to replace the spaces
                                    // again do prevent regex error.
                                    str = str.replace(/%20/g, ' ');
                                    
                                    if (values.format === 1) {

                                        // 46° 57.1578 N 7° 26.1102 E

                                        pattern = /(\d+)[%B0\s]+(\d+\.\d+)\s*([NS])[%2C\s]+(\d+)[%B0\s]+(\d+\.\d+)\s*([WE])/i;
                                        matches = str.match(pattern);
                                        if (matches) {
                                            latsign = (matches[3]=='S') ? -1 : 1;
                                            longsign = (matches[6]=='W') ? -1 : 1;
                                            d1 = parseFloat(matches[1]);
                                            m1 = parseFloat(matches[2]);
                                            d2 = parseFloat(matches[4]);
                                            m2 = parseFloat(matches[5]);
                                            latitude = latsign * (d1 + (m1/60.0));
                                            longitude = longsign * (d2 + (m2/60.0));
                                            lonlat = new OpenLayers.LonLat(longitude, latitude);
                                        }
                                    } else if (values.format === 2) {

                                        // 46° 57' 9.468" N 7° 26' 6.612" E

                                        pattern = /(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([NS])[%2C\s]+(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([WE])/i;
                                        matches = str.match(pattern);
                                        if (matches) {
                                            latsign = (matches[4]=='S') ? -1 : 1;
                                            longsign = (matches[8]=='W') ? -1 : 1;
                                            d1 = parseFloat(matches[1]);
                                            m1 = parseFloat(matches[2]);
                                            s1 = parseFloat(matches[3]);
                                            d2 = parseFloat(matches[5]);
                                            m2 = parseFloat(matches[6]);
                                            s2 = parseFloat(matches[7]);
                                            latitude = latsign * (d1 + (m1/60.0) + (s1/(60.0*60.0)));
                                            longitude = longsign * (d2 + (m2/60.0) + (s2/(60.0*60.0)));
                                            lonlat = new OpenLayers.LonLat(longitude, latitude);
                                        }
                                    } else if (values.format === 3) {

                                        // N 46° 57.1578 E 7° 26.1102

                                        pattern = /([NS])\s*(\d+)[%B0\s]+(\d+\.\d+)[%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+\.\d+)/i;
                                        matches = str.match(pattern);
                                        if (matches) {
                                            latsign = (matches[1]=='S') ? -1 : 1;
                                            longsign = (matches[4]=='W') ? -1 : 1;
                                            d1 = parseFloat(matches[2]);
                                            m1 = parseFloat(matches[3]);
                                            d2 = parseFloat(matches[5]);
                                            m2 = parseFloat(matches[6]);
                                            latitude = latsign * (d1 + (m1/60.0));
                                            longitude = longsign * (d2 + (m2/60.0));
                                            lonlat = new OpenLayers.LonLat(longitude, latitude);
                                        }
                                    } else if (values.format === 4) {

                                        // N 46° 57' 9.468" E 7° 26' 6.612"

                                        pattern = /([NS])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)/i;
                                        matches = str.match(pattern);
                                        if (matches) {
                                            latsign = (matches[1]=='S') ? -1 : 1;
                                            longsign = (matches[5]=='W') ? -1 : 1;
                                            d1 = parseFloat(matches[2]);
                                            m1 = parseFloat(matches[3]);
                                            s1 = parseFloat(matches[4]);
                                            d2 = parseFloat(matches[6]);
                                            m2 = parseFloat(matches[7]);
                                            s2 = parseFloat(matches[8]);
                                            latitude = latsign * (d1 + (m1/60.0) + (s1/(60.0*60.0)));
                                            longitude = longsign * (d2 + (m2/60.0) + (s2/(60.0*60.0)));
                                            lonlat = new OpenLayers.LonLat(longitude, latitude);
                                        }
                                    } else if (values.format === 5) {
                                        
                                        // 46.95263, 7.43517
                                        
                                        pattern = /(\d+\.\d+)[%2C\s]+(\d+\.\d+)/i;
                                        matches = str.match(pattern);
                                        if (matches) {
                                            lonlat = new OpenLayers.LonLat(matches[2], matches[1]);
                                        }
                                    }

                                    if (lonlat != null) {
                                        // Coordinates were parsed, put on map
                                        var WGS84 = new OpenLayers.Projection("EPSG:4326");
                                        me.addLonlatToMap(lonlat, WGS84);
                                        win.close();
                                    } else {
                                        // Show error panel
                                        var panel = this.up('form').query('panel[itemId=coordinatesError]');
                                        if (panel.length > 0) {
                                            panel[0].show();
                                        }
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        });
        win.show();
    },

    /**
     * Put a point on the map based on lonlat coordinates. If a projection is
     * provided the coordinates will be transformed before they are put on the
     * map.
     */
    addLonlatToMap: function(lonlat, projection) {

        // Transform if necessary
        if (projection && projection.getCode() != 'EPSG:900913') {
            lonlat = lonlat.transform(
                projection,
                new OpenLayers.Projection("EPSG:900913")
            );
        }

        // Center the map
        var map = this.getMapPanel().getMap();
        map.setCenter(lonlat);

        // Activate draw controls and put the point on the map
        var controls = map.getControlsBy('type', 'createPointControl');
        if (controls && controls[0]) {
            var createPointControl = controls[0];
            createPointControl.activate();
            createPointControl.drawFeature(
                new OpenLayers.Geometry.Point(lonlat.lon, lonlat.lat)
            );
        }
    },

    initEditorControls: function() {
        var mappanel = this.getMapPanel();
        var map = mappanel.getMap();

        var me = this;

        // The DragFeature control to move newly added activtiies
        var movePointCtrl = new OpenLayers.Control.DragFeature(mappanel.getVectorLayer(),{
            onComplete: function(feature, pixel){
                mappanel.setNewFeatureGeometry(feature.geometry);
            }
        });
        map.addControl(movePointCtrl);

        /*var moveAction = Ext.create('GeoExt.Action', {
            disabled: true,
            control: movePointCtrl,
            iconCls: 'move-button',
            map: map,
            scale: 'medium',
            text: 'Edit location',
            toggleGroup: 'map-controls',
            toggleHandler: function(button, state){
                if(state){
                    // Activate the DrawFeature control
                    movePointCtrl.activate();
                } else {
                    movePointCtrl.deactivate();
                }
            }
        });
        var moveButton = Ext.create('Ext.button.Button', moveAction);
        var tbar = mappanel.getDockedItems('toolbar')[0];
        tbar.insert(0, moveButton);*/

        // Add the control and button to create a new activity
        var createPointCtrl = new OpenLayers.Control.DrawFeature(
            mappanel.getVectorLayer(),
            OpenLayers.Handler.Point,{
                eventListeners: {
                    'featureadded': function(event){
                        var g = event.feature.geometry;
                        // Select the newly created point in order to be able
                        // to move it.
                        this.getNewFeatureSelectCtrl().select(event.feature);
                        // Deactivate the create point control
                        createPointCtrl.deactivate();
                        // But activate the move point control
                        movePointCtrl.activate();
                        // Store the new activity geometry to the mappanel
                        this.setNewFeatureGeometry(g);
                    },
                    scope: mappanel
                },
                'type': 'createPointControl'
            });
        map.addControl(createPointCtrl);

        // Allow only one feature at a time
        mappanel.getVectorLayer().events.register('beforefeatureadded',
            mappanel.getVectorLayer(), function(event){
                this.removeAllFeatures();
            });

        // When feature is selected, show popup
        mappanel.getVectorLayer().events.register('featureselected',
            mappanel.getVectorLayer(), function(event) {
                me.createPopup(event.feature);
            });
    },

    createPopup: function(feature) {

        var configStore = Ext.create('Lmkp.store.ActivityConfig');
        configStore.load();

        var popup = Ext.create('GeoExt.window.Popup', {
            itemId: 'mappopup',
            title: Lmkp.ts.msg('activities_new-title'),
            location: feature,
            unpinnable: false,
            draggable: true,
            layout: 'fit',
            width: 300,
            items: [
            {
                xtype: 'form',
                border: 0,
                bodyPadding: 5,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [
                    {
                        xtype: 'container',
                        html: '<p>' + Lmkp.ts.msg('activities_new-step-1-explanation') + '</p>'
//                    }, {
//                        xtype: 'textfield',
//                        value: 'Spatial Accuracy soon to come ...'
                    }
                ]
            }
            ],
            bbar: ['->',
            {
                xtype: 'button',
                itemId: 'mapPopupContinueButton',
                text: Lmkp.ts.msg('button_continue')
            }
            ]
        });
        popup.show();
    },

    /**
     * Return the geometry of the newly created activity (stored in map's
     * 'newFeatureGeometry' config).
     * {transform}: Optional parameter. Set to 'true' transforms the geometry to
     * the map's geographic Projection.
     */
    getActivityGeometryFromMap: function(transform) {
        var map = this.getMapPanel();
        var geom = map.getNewFeatureGeometry();
        if (geom && transform == true) {
            geom.transform(
                map.sphericalMercatorProjection,
                map.geographicProjection
                );
        }
        return geom;
    }

});