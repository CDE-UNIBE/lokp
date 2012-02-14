Ext.define('Lmkp.controller.manage.Main',{
    extend: 'Ext.app.Controller',

    /**
     * Activities form panel
     * @type Ext.form.Panel
     */
    activitiesDetailsPanel: null,

    models: [
    'Activity'
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
            }
        });
    },

    onPanelRendered: function(comp){
        this.activitiesDetailsPanel = comp;
        Ext.Ajax.request({
            url: '/config',
            params: {
                format: 'ext'
            },
            method: 'GET',
            success: function(response){
                var text = response.responseText;
                comp.add(Ext.decode(text));
            }
        });
    },

    onButtonClick: function(button, evt, eOpts){
        console.log(button, evt, eOpts);
    },

    onItemclick: function(view, record, item, index, event, eOpts){
        if(this.activitiesDetailsPanel){
            this.activitiesDetailsPanel.loadRecord(record);
        }
    }
    
});