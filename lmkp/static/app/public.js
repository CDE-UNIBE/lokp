Ext.onReady(function(){
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.public.Outer',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: ['login.Toolbar'],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'center',
                    xtype: 'lo_publicouterpanel'
                }]
            });
        }
    });
});