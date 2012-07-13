Ext.define('Lmkp.controller.moderator.Pending', {
    extend: 'Ext.app.Controller',

    stores: [
    'PendingActivityGrid'
    ],

    init: function(){
        this.control({
            'lo_moderatorpendingpanel': {
                render: this.onRender
            }
        });
    },

    onRender: function(comp){
        this.getPendingActivityGridStore().load();
    }
});