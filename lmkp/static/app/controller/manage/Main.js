Ext.define('Lmkp.controller.manage.Main',{
    extend: 'Ext.app.Controller',

    models: [
    'Activity'
    ],

    stores: [
    'Activities'
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
                render: this.onTreePanelRendered,
                checkchange: this.onCheckchange
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

    onTreePanelRendered: function(comp){
            
        /*this.getActivityTreeStore().load();*/

        console.log("ActivitiesStore: ", this.getActivitiesStore());
        this.getActivitiesStore().load({
            scope: this,
            callback: function(){
                console.log("ActivitiesStore^2: ", this.getActivitiesStore());
            }
        });
},

onButtonClick: function(button, evt, eOpts){
    console.log(button, evt, eOpts);
},

onCheckchange: function(node, checked, eOpts){
    console.log(node);
    var view = this.getManageMainPanelView();
    console.log(view);
}
    
});