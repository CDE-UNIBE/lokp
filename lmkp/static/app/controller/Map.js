Ext.define('Lmkp.controller.Map',{
    extend: 'Ext.app.Controller',

    stores: [
        'Profiles'
    ],

    views: [
        'MapPanel'
    ],

    init: function(){

        this.getProfilesStore().on('load', this.onLoad, this);

        this.control({
            'mappanel': {
                render: this.onPanelRendered
            }
        });
    },

    onLoad: function(store, records, successful, operation, eOpts) {
        var activeProfile = store.getAt(store.findExact('active', true));

        var geoJson = new OpenLayers.Format.GeoJSON();

        var feature = geoJson.read(Ext.encode(activeProfile.get('geometry')))[0];

        var mappanel = Ext.ComponentQuery.query('mappanel')[0];
        var map = mappanel.getMap();

        var geom = feature.geometry.clone().transform(
        new OpenLayers.Projection("EPSG:4326"),
        new OpenLayers.Projection("EPSG:900913"));

        map.zoomToExtent(geom.getBounds());
    },

    onPanelRendered: function(comp){

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

        // Add the controls to the map and activate them
        map.addControl(highlightCtrl);
        map.addControl(selectCtrl);

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


    },

    /*
     * Method on map move end.
     */
    onMoveEnd: function(event){
        // Move paging to back to page 1 when filtering (otherwise may show empty page instead of results)
        Ext.ComponentQuery.query('pagingtoolbar[id=activityGridPagingToolbar]')[0].moveFirst();
    },

    /**
     * Method triggered by the onfeatureunselected event by an OpenLayers.Layer.Vector
     */
    onFeatureUnselected: function(event){
        var grid = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
        grid.getSelectionModel().deselectAll(true);
    },

    /**
     * Method triggered by the onfeatureselected event by an OpenLayers.Layer.Vector
     */
    onFeatureSelected: function(event){
        // Get the GridPanel
        var grid = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
        //grid.getSelectionModel().deselectAll(true);
        var store = grid.getStore();

        // Get the record from the store with the same id as the selected vector
        var index = store.findBy(function(record, id){
            return event.feature.data.id == id;
        });
        var record = store.getAt(index);
        grid.getSelectionModel().select([record], false, true);

        var detailPanel = Ext.ComponentQuery.query('filterPanel detailPanel')[0];
        var selectedTab = detailPanel.getActiveTab();
        switch (selectedTab.getXType()) {
            case "activityHistoryTab":
                // var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
                // this._populateHistoryTab(selectedTab, uid)
                console.log("coming soon");
                break;
            default:
                // default is: activityDetailTab
                detailPanel.populateDetailsTab(selectedTab, [record]);
                break;
        }
    }

    
})