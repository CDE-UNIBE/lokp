Ext.define('Lmkp.controller.editor.GxMap', {
    extend: 'Ext.app.Controller',

    requires: [
    'Lmkp.model.Activity',
    'Lmkp.model.TagGroup',
    'Lmkp.model.Tag',
    'Lmkp.model.MainTag',
    'Lmkp.model.Point'
    ],

    stores: [
    'Profiles',
    'ActivityGrid'
    ],

    views: [
    'editor.GxMap',
    ],

    init: function() {
        this.control({
            'lo_editorgxmappanel': {
                render: this.onRender
            }
        });
    },

    onRender: function(comp){

        OpenLayers.ProxyHost = "/wms?url=";

        // Get the toolbar
        var tbar = comp.getDockedItems('toolbar')[0];
        // Get the map
        var map = comp.getMap();

        // Get the vecotr layer
        var vectorLayer = comp.getVectorLayer();

        // Register the featureselected event
        vectorLayer.events.register('featureselected', this, this.onFeatureSelected);
        vectorLayer.events.register('featureunselected', this, this.onFeatureUnselected);

        // Create the highlight and select control
        var highlightCtrl = new OpenLayers.Control.SelectFeature(vectorLayer, {
            id: 'highlightControl',
            hover: true,
            highlightOnly: true,
            renderIntent: "temporary"
        });

        var selectCtrl = new OpenLayers.Control.SelectFeature(vectorLayer, {
            id: 'selectControl',
            clickout: true
        });

        var identifyCtrl = new OpenLayers.Control.WMSGetFeatureInfo({
            eventListeners: {
                'getfeatureinfo': this.onGetFeatureInfo
            },
            infoFormat: 'application/vnd.ogc.gml',
            layers: [comp.getActivitiesLayer()],
            title: 'Identify features by clicking',
            url: 'http://localhost:8080/geoserver/lo/wms'
        });

        // Add the controls to the map and activate them
        map.addControl(highlightCtrl);
        map.addControl(selectCtrl);
        map.addControl(identifyCtrl);

        highlightCtrl.activate();
        selectCtrl.activate();

        var dragPanAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.DragPan({
                id: 'pan'
            }),
            map: map,
            iconCls: 'pan-button',
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: 'Pan'
        });
        tbar.add(Ext.create('Ext.button.Button', dragPanAction));

        var zoomBoxAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.ZoomBox({
                id: 'zoombox',
                type: OpenLayers.Control.TYPE_TOGGLE
            }),
            map: map,
            iconCls: 'zoom-in-button',
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: 'Zoom in'
        });
        tbar.add(Ext.create('Ext.button.Button', zoomBoxAction));

        tbar.add(Ext.create('Ext.button.Button', {
            handler: function(button, event, eOpts){
                this.zoomToProfile(map);
            },
            iconCls: 'zoom-region-button',
            scale: 'medium',
            scope: this,
            tooltip: 'Zoom to profile region'
        }));

        var identifyAction = Ext.create('GeoExt.Action',{
            control: identifyCtrl,
            handler: identifyAction,
            iconCls: 'identify-button',
            map: map,
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: "Identify feature"
        });
        tbar.add(Ext.create('Ext.button.Button', identifyAction));

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

        // Reload the ActivityGrid store
        this.getActivityGridStore().load();
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

    onGetFeatureInfo: function(event){
        var gml = new OpenLayers.Format.GML();
        // Get the first vector
        var vector = gml.read(event.text)[0];
        if(!vector){
            return;
        }
        var identifier = vector.data.activity_identifier;
        Ext.Ajax.request({
            url: '/activities/' + identifier,
            success: function(response){
                var responseObj = Ext.decode(response.responseText);

                // Create a temporary memory store to properly
                // read the server response
                var store = Ext.create('Ext.data.Store', {
                    autoLoad: true,
                    model: 'Lmkp.model.Activity',
                    data : responseObj,
                    proxy: {
                        type: 'memory',
                        reader: {
                            root: 'data',
                            type: 'json',
                            totalProperty: 'total'
                        }
                    }
                });

                var detailPanels = Ext.ComponentQuery.query('lo_editordetailpanel');
                for(var i = 0; i < detailPanels.length; i++) {
                    var activeTab = detailPanels[i].getActiveTab();
                    switch (activeTab.getXType()) {
                        case "activityHistoryTab":
                            // var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
                            // detailPanel._populateHistoryTab(selectedTab, uid)
                            console.log("coming soon");
                            break;
                        default: 	// default is: activityDetailTab
                            //console.log(activity);
                            detailPanels[i].populateDetailsTab(activeTab, [store.getAt(0)]);
                            break;
                    }
                }
                
            }
        });
    }

});