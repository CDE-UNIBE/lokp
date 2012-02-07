Ext.define('Lmkp.controller.manage.Main',{
    extend: 'Ext.app.Controller',

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
            }
        });
    },

    onPanelRendered: function(comp){
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
    }
    
});