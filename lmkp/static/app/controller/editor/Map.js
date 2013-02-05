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