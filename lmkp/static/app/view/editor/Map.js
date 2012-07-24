Ext.define('Lmkp.view.editor.Map',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.lo_editormappanel'],

    requires: [
    'GeoExt.Action'
    ],

    border: false,
    frame: false,

    // Initial center
    center: new OpenLayers.LonLat(0,0),

    config: {
        activitiesLayer: null,
        baseLayer: null,
        identifyCtrl: null,
        map: null,
        vectorLayer: null
    },

    layout: 'fit',

    geographicProjection: new OpenLayers.Projection("EPSG:4326"),

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),

    // Toolbar
    tbar: null,

    // Initial zoom level
    zoom: 2,

    initComponent: function() {

        // Proxy host
        OpenLayers.ProxyHost = "/wms?url=";
        
        this.baseLayer = new OpenLayers.Layer.OSM('mapnik', null, {
            sphericalMercator: true,
            projection: new OpenLayers.Projection("EPSG:900913")
        });
        
        this.activitiesLayer = new OpenLayers.Layer.WMS('Activities',
            'http://localhost:8080/geoserver/lo/wms',{
                layers: 'activities',
                transparent: true,
                format: 'image/png8',
                epsg: 900913
            },{
                isBaseLayer: false,
                sphericalMercator: true,
                maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
                    20037508.34, 20037508.34)
            });

        this.vectorLayer = new OpenLayers.Layer.Vector('pointLayer',{
            isBaseLayer: false
        });

        // The map
        this.map = new OpenLayers.Map({
            displayProjection: this.geographicProjection,
            controls: [
            new OpenLayers.Control.Navigation()
            ],
            layers: [
            this.baseLayer,
            this.activitiesLayer,
            this.vectorLayer
            ],
            projection: this.sphericalMercatorProjection
        });


        // Create the toolbar
        this.tbar = Ext.create('Ext.toolbar.Toolbar',{
            dock: 'top'
        });

        this.identifyCtrl = new OpenLayers.Control.WMSGetFeatureInfo({
            infoFormat: 'application/vnd.ogc.gml',
            layers: [this.activitiesLayer],
            title: 'Identify features by clicking',
            url: 'http://localhost:8080/geoserver/lo/wms'
        });



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

        this.callParent(arguments);
    }

});