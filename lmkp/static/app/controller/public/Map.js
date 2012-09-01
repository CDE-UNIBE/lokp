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
        var me = this;
       	
       	// Make sure that ActivityGridStore does not display any Stakeholders 
       	// (return_sh). Also refresh if Activities were shown based on a 
       	// Stakeholder (sh_id). Also set EPSG again
       	var params = this.getActivityGridStore().getProxy().extraParams;
       	if (!params['return_sh'] || params['sh_id'] || !params['epsg']) {
	        delete params.return_sh;
	        delete params.sh_id;
	        params['epsg'] = 900913;
	        this.getActivityGridStore().getProxy().extraParams = params;
       	}
       	
        this.getActivityGridStore().load(function() {
        	// Update StakeholderGrid store to match ActivityGrid
        	var shStore = me.getStakeholderGridStore();
        	shStore.syncWithActivities(this.getProxy().extraParams);
        });
    }

});