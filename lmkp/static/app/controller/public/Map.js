Ext.define('Lmkp.controller.public.Map', {
    extend: 'Ext.app.Controller',
    
    refs: [{
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
    }],

    stores: [
    'ActivityGrid',
    'Profiles',
    'StakeholderGrid'
    ],

    config: {
        geojson: {}
    },
    geojson: new OpenLayers.Format.GeoJSON(),

    init: function() {
        this.control({
            'lo_publicmappanel': {
                render: this.onMapPanelRender
            },
            'lo_publicmappanel button[itemId="zoomRegionButton"]': {
                click: this.onZoomRegionButtonClick
            }
        });
    },

    onZoomRegionButtonClick: function(button, event, eOpts){
        this.zoomToProfile(this.getMapPanel().getMap());
    },

    zoomToProfile: function(map) {

        var store = this.getProfilesStore();
        var activeProfile = store.getAt(store.findExact('active', true));
        if(activeProfile){
            var geoJson = new OpenLayers.Format.GeoJSON();

            var feature = geoJson.read(Ext.encode(activeProfile.get('geometry')))[0];

            var geom = feature.geometry.clone().transform(
                new OpenLayers.Projection("EPSG:4326"),
                new OpenLayers.Projection("EPSG:900913"));

            map.zoomToExtent(geom.getBounds());
        }

    },

    onMapPanelRender: function(comp){
        // Get the map
        var map = comp.getMap();

        // Get the map center and zoom level from the cookies if one is set
        var location = Ext.util.Cookies.get('_LOCATION_');
        if(location){
            var values = location.split('|');
            map.setCenter(new OpenLayers.LonLat(values[0], values[1]));
            map.zoomTo(values[2]);
        }

        // Register the moveend event with the map
        // after setting map center and zoom level
        map.events.register('moveend', this, this.onMoveEnd);

        // If logged in, show controls for editors (add or edit location etc.)
        if (Lmkp.toolbar != false) {
            var editorMapController = this.getController('editor.Map');
            editorMapController.initEditorControls();
        }

        var ctrl = comp.getIdentifyCtrl();
        ctrl.events.register('featurehighlighted', comp, function(event){
            var f = event.feature
            if (f) {
                // Show details window
                var w = Ext.create('Lmkp.view.activities.Details',{
                    activity_identifier: f.attributes.activity_identifier
                }).show()._collapseHistoryPanel();
                w.on('close', function(panel){
                    this.unselectAll();
                }, ctrl);
            }
        });
    },

    onMoveEnd: function(event){
        // Store the current map center and zoom level as cookie in the format:
        // longitude|latitude|zoom
        // and set the expiration date in three month
        var map = event.object;
        var center = map.getCenter();
        var zoom = map.getZoom();
        var value = center.lon + "|" + center.lat + "|" + zoom;

        var expirationDate = new Date();
        expirationDate.setMonth(new Date().getMonth() + 3);
        Ext.util.Cookies.set('_LOCATION_', value, expirationDate);

        // Reload the ActivityGrid store. Also refresh StakeholderGrid.
        var aStore = this.getActivityGridStore();
        var shStore = this.getStakeholderGridStore();

        aStore.setInitialProxy();
        this.getActivityGridStore().loadPage(1, {
            callback: function() {
                // Update StakeholderGrid store to match ActivityGrid
                shStore.syncWithActivities(this.getProxy().extraParams);
            }
        });
    },

    showActivityOnMap: function(activity) {

        // Make sure item is an 'Activity'
        if (activity.modelName == 'Lmkp.model.Activity') {
            var vLayer = this.getMapPanel().getVectorLayer();

            // Assumption: only one activity can be shown at a time
            vLayer.removeAllFeatures();
            var features = this._getVectorsFromActivity(activity);
            if (features) {
                vLayer.addFeatures(features);
            }
        }
    },

    _getVectorsFromActivity: function(activity) {

        // Make sure item is an 'Activity'
        if (activity.modelName != 'Lmkp.model.Activity') {
            return null;
        }

        // Collect vectors, transform and return them
        var geom = activity.get('geometry');
        var map = this.getMapPanel();
        var vectors = this.geojson.read(Ext.encode(geom));
        if (vectors) {
            for(var j = 0; j < vectors.length; j++){
                vectors[j].geometry.transform(
                    map.geographicProjection,
                    map.sphericalMercatorProjection
                    );
            }
            return vectors;
        }
    }

});