Ext.application({
    name: 'Lmkp',
    appFolder: 'static/app',

    controllers: Lmkp.mainControllers,
    //controllers: ['Main', 'Layers', 'Map', 'Filter', 'EditFilter'],
    
    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: {
                type: 'border',
                padding: 0
            },
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
