Ext.application({
    name: 'LMKP',
    appFolder: 'static/app',

    controllers: [
    'Main',
    'Layers'
    ],

    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [{
                height: 100,
                region: 'north',
                xtype: 'header'
            },{
                region: 'center',
                xtype: 'main'
            }]
        });
    }
});