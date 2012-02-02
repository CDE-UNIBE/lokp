Ext.application({
    name: 'Lmkp',
    appFolder: 'static/app',

    controllers: [
    'manage.Main'
    ],

    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [{
                height: 40,
                region: 'north',
                xtype: 'header'
            },{
                region: 'center',
                xtype: 'managemainpanel'
            }]
        });
    }
});