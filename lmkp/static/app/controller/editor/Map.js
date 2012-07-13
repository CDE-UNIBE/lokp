Ext.define('Lmkp.controller.editor.Map', {
    extend: 'Ext.app.Controller',

    requires: [
    'Lmkp.model.Activity',
    'Lmkp.model.TagGroup',
    'Lmkp.model.Tag',
    'Lmkp.model.MainTag',
    'Lmkp.model.Point'
    ],

    stores: [
    'Profiles'
    ],

    views: [
    'editor.Map',
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

        this.getProfilesStore().on('load', this.onLoad, this);

        // Get the toolbar
        var tbar = comp.getDockedItems('toolbar')[0];
        // Get the map
        var map = comp.getMap();

        // Register the moveend event with the map
        map.events.register('moveend', this, this.onMoveEnd);

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
            toggleGroup: 'map-controls'
        });
        tbar.add(Ext.create('Ext.button.Button', dragPanAction));

        var zoomBoxAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.ZoomBox({
                id: 'zoombox',
                type: OpenLayers.Control.TYPE_TOGGLE
            }),
            map: map,
            iconCls: 'zoom-in-button',
            toggleGroup: 'map-controls'
        });
        tbar.add(Ext.create('Ext.button.Button', zoomBoxAction));

        tbar.add(Ext.create('Ext.button.Button', {
            handler: function() {
                var selectedFeatures = new Array();
                var layers = map.getLayersByClass('OpenLayers.Layer.Vector');
                for(var i = 0; i < layers.length; i++){
                    for(var j = 0; j < layers[i].selectedFeatures.length; j++){
                        selectedFeatures.push(layers[i].selectedFeatures[j]);
                    }

                }

                console.log(selectedFeatures[0]);
                var bounds = selectedFeatures[0].geometry.getBounds().clone();

                for(var i = 1; i < selectedFeatures.length; i++) {
                    bounds.extend(selectedFeatures[i].geometry.getBounds());
                }

                map.zoomToExtent(bounds);

            },
            iconCls: 'zoom-to-selected'
        }));

        var identifyAction = Ext.create('GeoExt.Action',{
            control: identifyCtrl,
            iconCls: 'identify-feature',
            map: map,
            toggleGroup: 'map-controls'
        });
        tbar.add(Ext.create('Ext.button.Button', identifyAction));
    },

    onLoad: function(store, records, successful, operation, eOpts) {
        var activeProfile = store.getAt(store.findExact('active', true));

        var geoJson = new OpenLayers.Format.GeoJSON();

        var feature = geoJson.read(Ext.encode(activeProfile.get('geometry')))[0];

        var mappanel = Ext.ComponentQuery.query('lo_editorgxmappanel')[0];
        var map = mappanel.getMap();

        var geom = feature.geometry.clone().transform(
            new OpenLayers.Projection("EPSG:4326"),
            new OpenLayers.Projection("EPSG:900913"));

        map.zoomToExtent(geom.getBounds());
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

                var detailPanel = Ext.ComponentQuery.query('lo_editormappanel lo_editordetailpanel')[0];
                var activeTab = detailPanel.getActiveTab();
                switch (activeTab.getXType()) {
                    case "activityHistoryTab":
                        // var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
                        // detailPanel._populateHistoryTab(selectedTab, uid)
                        console.log("coming soon");
                        break;
                    default: 	// default is: activityDetailTab
                        //console.log(activity);
                        detailPanel.populateDetailsTab(activeTab, [store.getAt(0)]);
                        break;
                }
            }
        });

    }

});