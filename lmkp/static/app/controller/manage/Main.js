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
            'managemainpanel toolbar combobox[id*=locale-combobox]': {
                change: this.onCountryChange
            }
        });
    },

    onPanelRendered: function(comp){

        // Request a configuration object from the /config controller to append
        // more form textfields to the activity detail form
        Ext.Ajax.request({
            url: '/config',
            params: {
                format: 'ext'
            },
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

                // Update the map panel
                console.log(this.getMapPanel().map);
            },
            scope: this
        });
    },

    onButtonClick: function(button, evt, eOpts){
        console.log(button, evt, eOpts);

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
            console.log(records);
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
                    Ext.Msg.alert('HTTP Success Status', action.response.statusText);
                },
                url: '/activities/' + id
            });
        }
    },

    onMainPanelRendered: function(comp){
        console.log("kdkd");

        var translationsStore = Ext.data.StoreManager.lookup('translations');
        if(!translationsStore)
            translationsStore = Ext.create('Lmkp.store.Translations', {
                listeners: {
                    load: {
                        fn: function(store, records, successful, operation, eOpts){
                            console.log(store.getById('pan-button'));
                        }
                    }
                }
            });


    //        console.log(translationsStore);
    //        console.log(translationsStore.getById2('pan-button'));

    },

    /**
     * Fires after an country
     */
    onCountryChange: function(field, newValue, oldValue, eOpts){
        var form = Ext.create('Ext.form.Panel', {
            standardSubmit: true,
            url: '/manage'
        });
        form.submit({
            params: {
                locale: newValue
            }
        });
    }

});