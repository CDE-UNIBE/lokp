Ext.define('Lmkp.view.public.Map',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.lo_publicmappanel'],

    requires: [
    'GeoExt.Action',
    'Lmkp.view.public.BaseLayers',
    'Lmkp.view.public.ContextLayers'
    ],

    //border: false,
    frame: false,

    // Initial center
    center: new OpenLayers.LonLat(0,0),

    config: {
        activitiesLayer: null,
        baseLayers: null,
        identifyCtrl: null,
        map: null,
        vectorLayer: null,
        activityGeometry: null,
        vectorStore: null
    },

    layout: 'fit',

    geographicProjection: new OpenLayers.Projection("EPSG:4326"),

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),

    // Toolbar
    tbar: null,

    // Initial zoom level
    zoom: 2,

    initComponent: function() {
        
        this.activitiesLayer = new OpenLayers.Layer.Vector('Activities', {
            isBaseLayer: false,
            maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
                20037508.34, 20037508.34),
            sphericalMercator: true
        });

        this.vectorLayer = new OpenLayers.Layer.Vector('pointLayer',{
            isBaseLayer: false
        });

        this.vectorStore = Ext.create('Lmkp.store.ActivityVector',{
            autoLoad: true,
            layer: this.activitiesLayer,
            proxy: Ext.create('GeoExt.data.proxy.Protocol',{
                protocol: new OpenLayers.Protocol.HTTP({
                    format: new OpenLayers.Format.GeoJSON({
                        externalProjection: this.geographicProjection,
                        internalProjection: this.sphericalMercatorProjection
                    }),
                    url: "/activities/geojson"
                }),
                reader: {
                    root: 'features',
                    type: 'feature'
                }
            })
        });

        this.vectorStore.on('load', function(store, records, successful){
            //console.log(this.activitiesLayer);
            }, this);

        // Create the map, the layers are appended later, see below.
        this.map = new OpenLayers.Map({
            displayProjection: this.geographicProjection,
            controls: [
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.Navigation()
            ],
            projection: this.sphericalMercatorProjection
        });


        // Create the toolbar
        this.tbar = Ext.create('Ext.toolbar.Toolbar',{
            dock: 'top',
            itemId: 'mapPanelToolbar'
        });

        // Create the identify control and action
        this.identifyCtrl = new OpenLayers.Control.SelectFeature(this.activitiesLayer);

        // Add the controls to the map
        this.map.addControl(this.identifyCtrl);

        var panAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.DragPan({
                id: 'pan'
            }),
            map: this.map,
            iconCls: 'pan-button',
            pressed: true,
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: 'Pan'
        });
        var panButton = Ext.create('Ext.button.Button', panAction);
        this.tbar.add(panButton);

        var zoomBoxAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.ZoomBox({
                id: 'zoombox',
                type: OpenLayers.Control.TYPE_TOGGLE
            }),
            map: this.map,
            iconCls: 'zoom-in-button',
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: 'Zoom in'
        });
        this.tbar.add(Ext.create('Ext.button.Button', zoomBoxAction));

        var zoomOutAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.ZoomOut(),
            map: this.map,
            iconCls: 'zoom-out-button',
            scale: 'medium',
            tooltip: 'Zoom out'
        });
        this.tbar.add(Ext.create('Ext.button.Button', zoomOutAction));

        this.tbar.add(Ext.create('Ext.button.Button', {
            iconCls: 'zoom-region-button',
            itemId: 'zoomRegionButton',
            scale: 'medium',
            scope: this,
            tooltip: 'Zoom to profile region'
        }));

        var identifyAction = Ext.create('GeoExt.Action',{
            control: this.identifyCtrl,
            handler: identifyAction,
            iconCls: 'identify-button',
            map: this.map,
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: "Identify feature"
        });
        this.tbar.add(Ext.create('Ext.button.Button', identifyAction));

        this.tbar.add('->');

        // Create the base layer menu. This class will append the base layers
        // to the map
        var baseLayerMenu = Ext.create('Lmkp.view.public.BaseLayers',{
            map: this.map
        });
        // And add it to the toolbar
        this.tbar.add({
            text: Lmkp.ts.msg('Base Layers'),
            menu: baseLayerMenu
        });

        // Now add the WMS layer showing the activities and the vector layer
        // that is used when selecting activities.
        // Order matters!
        this.map.addLayers([this.activitiesLayer, this.vectorLayer]);

        // Create the context layers menu. It will append the context layers to
        // the map
        var contextLayersMenu = Ext.create('Lmkp.view.public.ContextLayers', {
            parent: this
        });
        // Add the context layers to the toolbar.
        this.tbar.add({
            text: Lmkp.ts.msg("Context Layers"),
            menu: contextLayersMenu
        });

        this.callParent(arguments);
    }

});