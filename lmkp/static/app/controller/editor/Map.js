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

    initEditorControls: function() {
        var mappanel = this.getMapPanel();
        var map = mappanel.getMap();
        var tbar = mappanel.getDockedItems('toolbar')[0];

        // Select
        var selectCtrl = new OpenLayers.Control.SelectFeature(
            mappanel.getVectorLayer()
        );

        // Add the control and button to move an activity
        var movePointCtrl = new OpenLayers.Control.ModifyFeature(
            mappanel.getVectorLayer(), {
                mode: OpenLayers.Control.ModifyFeature.DRAG,
                selectControl: selectCtrl
            });
        map.addControl(movePointCtrl);
        mappanel.getVectorLayer().events.register('featuremodified', mappanel,
            function(event) {
            var g = event.feature.geometry;
            this.setActivityGeometry(g);
        });
        var moveAction = Ext.create('GeoExt.Action', {
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
        tbar.insert(0, moveButton);

        // Add the control and button to create a new activity
        var createPointCtrl = new OpenLayers.Control.DrawFeature(
            mappanel.getVectorLayer(),
            OpenLayers.Handler.Point,{
                eventListeners: {
                    'featureadded': function(event){
                        var g = event.feature.geometry;
                        //selectCtrl.select(event.feature);
                        createPointCtrl.deactivate();
                        selectCtrl.select(event.feature);
                        movePointCtrl.activate();
                        movePointCtrl.selectFeature(event.feature);
                        moveButton.toggle(true);
                        this.setActivityGeometry(g);
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
        var me = this;
        mappanel.getVectorLayer().events.register('featureselected',
            mappanel.getVectorLayer(), function(event) {
                me.createPopup(event.feature);
            });
    },

    createPopup: function(feature) {

        var configStore = Ext.create('Lmkp.store.ActivityConfig');
        configStore.load();
        console.log(configStore);

        var popup = Ext.create('GeoExt.window.Popup', {
            itemId: 'mappopup',
            title: 'New Activity',
            location: feature,
            unpinnable: false,
            draggable: true,
            layout: 'fit',
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
                            html: '<p>You can drag and drop the point.</p><p>Once you are done, click "Continue".</p>'
                        }, {
                            xtype: 'textfield',
                            value: 'Spatial Accuracy soon to come ...'
                        }
                    ]
                }
            ],
            bbar: ['->',
                {
                    xtype: 'button',
                    itemId: 'mapPopupContinueButton',
                    text: 'Continue'
                }
            ]
        });
        popup.show();
    },

    /**
     * Return the geometry of the newly created activity (stored in map's
     * 'activityGeometry' config).
     * {transform}: Optional parameter. Set to 'true' transforms the geometry to
     * the map's geographic Projection.
     */
    getActivityGeometryFromMap: function(transform) {
        var map = this.getMapPanel();
        var geom = map.getActivityGeometry();
        if (geom && transform == true) {
            geom.transform(
                map.sphericalMercatorProjection,
                map.geographicProjection
            );
        }
        return geom;
    }

});