Ext.define('Lmkp.controller.manage.Main',{
    extend: 'Ext.app.Controller',

    views: [
    'manage.MainPanel',
    'manage.activities.Details',
    'manage.activities.TreePanel'
    ],

    init: function(){
        console.log(window);
        this.control({
            '#activity-details-panel': {
                render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function(comp){
        console.log(comp);
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
        
    }
    
});