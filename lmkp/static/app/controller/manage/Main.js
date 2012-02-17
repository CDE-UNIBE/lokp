Ext.define('Lmkp.controller.manage.Main',{
    extend: 'Ext.app.Controller',

    models: [
    'DyLmkp.model.Activity',
    'Lmkp.model.ActivityTree'
    ],

    refs: [{
        ref: 'detailsForm',
        selector: 'manageactivitiesdetails'
    }],

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
            }
        });
    },

    onButtonClick: function(button, evt, eOpts){
        console.log(button, evt, eOpts);
    },

    onItemclick: function(view, record, item, index, event, eOpts){
        if(!record.hasChildNodes()){
            var id = record.data.id;
            this.getDetailsForm().load({
                url: '/activities/' + id,
                method: 'GET',
                failure: function(form, action){
                    Ext.Msg.alert('HTTP Status', action.response.statusText);
                }
            });
        }
    }
});