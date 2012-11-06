Ext.define('Lmkp.view.public.Map',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.lo_publicmappanel'],

    requires: [
    'GeoExt.Action',
    'GeoExt.data.proxy.Protocol',
    'Lmkp.store.ActivityVector',
    'Lmkp.view.public.BaseLayers',
    'Lmkp.view.public.ContextLayers'
    ],

    //border: false,
    frame: false,

    // Initial center
    //    center: new OpenLayers.LonLat(0,0),

    config: {
        /**
         * An OpenLayers.Layer.Vector layer that holds all active activities
         * and pending changes of the logged in user.
         */
        activitiesLayer: null,
        /**
         * A GeoExt.data.FeatureStore that holds the features from activitesLayer
         */
        activityFeatureStore: null,
        baseLayers: null,
        /**
         * OpenLayers.Geometry that store the geometry of newly created activities
         */
        newFeatureGeometry: null,
        /**
         * A SelectFeature control to select newly set activities when creating
         * new activities.
         */
        newFeatureSelectCtrl: null,
        map: null,
        /**
         * A SelectFeature control to select activities.
         */
        selectCtrl: null,
        /**
         * Helper OpenLayers.Layer.Vector layer that is solely used when a new
         * activity is created
         */
        vectorLayer: null
    },

    layout: 'fit',

    geographicProjection: new OpenLayers.Projection("EPSG:4326"),

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),

    // Toolbar
    tbar: null,

    // Initial zoom level
    //    zoom: 2,

    initComponent: function() {

        var fillOpacity = 0.6;

        var rules = [
        // Rule for active Activities
        new OpenLayers.Rule({
            title: "Active Activities",
            filter: new OpenLayers.Filter.Comparison({
                property: 'status',
                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                value: 'active'
            }),
            symbolizer: {
                graphicName: "circle",
                pointRadius: 7,
                fillColor: "#bd0026",
                fillOpacity: fillOpacity,
                strokeColor: "#bd0026",
                strokeWidth: 1
            }
        }), new OpenLayers.Rule({
            title: "Pending Activities",
            filter: new OpenLayers.Filter.Comparison({
                property: 'status',
                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                value: 'pending'
            }),
            symbolizer: {
                graphicName: "triangle",
                pointRadius: 7,
                fillColor: "#ff6100",
                fillOpacity: fillOpacity,
                strokeColor: "#ff6100",
                strokeWidth: 1
            }
        })
        ];
        
        this.activitiesLayer = new OpenLayers.Layer.Vector('Activities', {
            isBaseLayer: false,
            maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
                20037508.34, 20037508.34),
            sphericalMercator: true,
            styleMap: new OpenLayers.StyleMap({
                "default": new OpenLayers.Style({}, {
                    rules: rules
                }),
                "select": new OpenLayers.Style({
                    fillColor: '#00ffff',
                    fillOpacity: 0.8,
                    strokeColor: '#006666'
                })
            })
        });

        this.vectorLayer = new OpenLayers.Layer.Vector('pointLayer',{
            isBaseLayer: false
        });

        this.activityFeatureStore = Ext.create('Lmkp.store.ActivityVector',{
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
        this.selectCtrl = new OpenLayers.Control.SelectFeature(this.activitiesLayer,{
            clickout: false,
            multiple: false
        });
        this.map.addControl(this.selectCtrl);

        // Create the identify control and action
        this.newFeatureSelectCtrl = new OpenLayers.Control.SelectFeature(this.vectorLayer);
        this.map.addControl(this.newFeatureSelectCtrl);

        var panAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.DragPan({
                id: 'pan'
            }),
            map: this.map,
            iconCls: 'pan-button',
            pressed: true,
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: Lmkp.ts.msg('tooltip_map_pan')
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
            tooltip: Lmkp.ts.msg('tooltip_map_zoom-in')
        });
        this.tbar.add(Ext.create('Ext.button.Button', zoomBoxAction));

        var zoomOutAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.ZoomOut(),
            map: this.map,
            iconCls: 'zoom-out-button',
            scale: 'medium',
            tooltip: Lmkp.ts.msg('tooltip_map_zoom-out')
        });
        this.tbar.add(Ext.create('Ext.button.Button', zoomOutAction));

        this.tbar.add(Ext.create('Ext.button.Button', {
            iconCls: 'zoom-region-button',
            itemId: 'zoomRegionButton',
            scale: 'medium',
            scope: this,
            tooltip: Lmkp.ts.msg('tooltip_map_zoom-to-profile-region')
        }));

        var selectAction = Ext.create('GeoExt.Action',{
            control: this.selectCtrl,
            handler: selectAction,
            iconCls: 'identify-button',
            map: this.map,
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: Lmkp.ts.msg('tooltip_map_identify-feature')
        });
        this.tbar.add(Ext.create('Ext.button.Button', selectAction));

        this.tbar.add('->');

        // Create the base layer menu. This class will append the base layers
        // to the map
        var baseLayerMenu = Ext.create('Lmkp.view.public.BaseLayers',{
            map: this.map
        });
        // And add it to the toolbar
        this.tbar.add({
            text: Lmkp.ts.msg('button_map_base-layers'),
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
            text: Lmkp.ts.msg('button_map_context-layers'),
            menu: contextLayersMenu
        });

        // Map center and zoom extent
        var location = Ext.util.Cookies.get('_LOCATION_');
        if (location) {
            // If a location is set in cookies, use this one
            var values = location.split('|');
            this.center = new OpenLayers.LonLat(values[0], values[1]);
            this.zoom = values[2];
        } else {
            // If no cookie is set, try to get information from current profile
            var profileExtent = Lmkp.currentProfileExtent;
            if (profileExtent) {
                var geojson = new OpenLayers.Format.GeoJSON()
                var feature = geojson.read(Ext.encode(profileExtent))[0];
                var bounds = feature.geometry.getBounds().clone();
                // Transform coordinates
                bounds.transform(
                    this.geographicProjection,
                    this.sphericalMercatorProjection
                    );
                this.extent = bounds;
            } else {
                // Fall back
                this.center = new OpenLayers.LonLat(0,0);
                this.zoom = 2;
            }
        }
        this.callParent(arguments);
    }

});