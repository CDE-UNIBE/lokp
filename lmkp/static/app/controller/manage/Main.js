Ext.define('Lmkp.controller.manage.Main',{
    extend: 'Ext.app.Controller',

    models: [
    'DyLmkp.model.Activity',
    'Lmkp.model.ActivityTree',
    'Lmkp.model.ActivityTest',
    'Lmkp.model.MessageString'
    ],

    refs: [{
        ref: 'detailsForm',
        selector: 'manageactivitiesdetails'
    },{
        ref: 'mapPanel',
        selector: 'managemainpanel mappanel'
    }],

    requires: [
    'Lmkp.reader.GeoJson',
    'Lmkp.store.Translations',
    'Lmkp.model.MessageString'
    ],

    views: [
    'manage.MainPanel',
    'manage.activities.Details',
    'manage.activities.TreePanel'
    ],

    init: function(){
        this.control({
            'manageactivitiesdetails': {
                render: this.onPanelRendered
            },
            // Select the submit button in the details view
            'manageactivitiesdetails button[text=Submit]': {
                click: this.onButtonClick
            },
            'manageactivitiestreepanel': {
                itemclick: this.onItemclick
            },
            'managemainpanel': {
                render: this.onMainPanelRendered
            },
            'managemainpanel mappanel': {
                render: this.onMapPanelRender
            },
            'managemainpanel toolbar combobox[id*=locale-combobox]': {
                change: this.onCountryChange
            },
            'managemainpanel [id=menubutton_config]': {
            	click: this.showConfigWindow
            }
        });
    },
    
    showConfigWindow: function() {
    	var win;
    	if (!win) {
    		win = Ext.create('widget.window', {
    			title: 'Configuration',
    			closable: true,
    			width: 400,
    			loader: {
    				url: '/config/scan',
    				contentType: 'html',
    				loadMask: true,
    				autoLoad: true
    			}
    		});
    	}
    	win.show();
    },

    onPanelRendered: function(comp){

        // Request a configuration object from the /config controller to append
        // more form textfields to the activity detail form
        Ext.Ajax.request({
            url: '/config/form',
            method: 'GET',
            success: function(response){
                var text = response.responseText;

                var configs = Ext.decode(text);

                for(var i = 0; i < configs.length; i++){
                    if(configs[i]['validator']){
                        // Create a validator functions from a string transmitted
                        // with JSON.
                        // The other fields are taken directly from /config
                        // controller's output
                        configs[i]['validator'] = new Function('value', configs[i]['validator']);
                    }
                }
                comp.add(configs);
                comp.doLayout();

            }
        });
    },

    onButtonClick: function(button, evt, eOpts){
        //console.log(button, evt, eOpts);

        //var test = Ext.create('Lmkp.model.ActivityTest');

        //console.log(test);

        var store = new Ext.create('Ext.data.JsonStore', {
            // store configs
            autoDestroy: true,
            storeId: 'myStore',

            proxy: {
                type: 'ajax',
                url: '/geojson',
                reader: 'geojson'
            },

            fields:[{
                name: 'id',
                type: 'int'
            },{
                name: 'name',
                type: 'string'
            }]
        });

        store.load(function(records, operation, success){
            //console.log(records);
        });

        

    },

    onItemclick: function(view, record, item, index, event, eOpts){
        if(!record.hasChildNodes()){
            var id = record.data.id;
            this.getDetailsForm().load({
                failure: function(form, action){
                    Ext.Msg.alert('HTTP Status', action.response.statusText);
                },
                method: 'GET',
                params: {
                    status: record.data.parentId
                },
                success: function(form, action){
                    //Ext.Msg.alert('HTTP Success Status', action.response.statusText);
                },
                url: '/activities/json/' + id
            });
        }
    },

    onMainPanelRendered: function(comp){

        var translationsStore = Ext.data.StoreManager.lookup('translations');
        if(!translationsStore)
            translationsStore = Ext.create('Lmkp.store.Translations', {
                listeners: {
                    load: {
                        fn: function(store, records, successful, operation, eOpts){
                            //console.log(store.getById('pan-button'));
                        }
                    }
                }
            });

    },

    /**
     * Fires after country selection
     */
    onCountryChange: function(field, newValue, oldValue, eOpts){
        var form = Ext.create('Ext.form.Panel', {
            standardSubmit: true,
            url: '/manage'
        });
        form.submit({
            params: {
                _LOCALE_: newValue
            }
        });
    },

    /**
     * Fires as soon as the map panel is rendered to update the map extent
     */
    onMapPanelRender: function(comp, eOpts){
        Ext.Ajax.request({
            url: '/config/bbox',
            method: 'GET',
            success: function(response){
                var configs = Ext.decode(response.responseText);
                var bounds = OpenLayers.Bounds.fromString(configs['bbox']);
                // Transform the geographic coordinates to spherical mercator projection
                bounds.transform(new OpenLayers.Projection('EPSG:4326'),
                    new OpenLayers.Projection('EPSG:900913'));
                // Zoom to this extent
                this.getMapPanel().map.zoomToExtent(bounds);
            },
            scope: this
        });

    }

});
