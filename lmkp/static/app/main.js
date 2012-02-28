Ext.application({
    name: 'Lmkp',
    appFolder: 'static/app',

    controllers: [
    'Main',
    'Layers',
    'Map',
    'Filter'
    ],

    launch: function() {
        console.log('launch');
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