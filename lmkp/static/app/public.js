Ext.onReady(function(){
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.Public',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: ['Outer', 'Main'],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'center',
                    xtype: 'lo_publicpanel'
                }]
            });
        }
    });
});