Ext.application({
    name: 'Lmkp',
    appFolder: 'static/app',

    requires: [
        'Lmkp.view.Outer',
        'Lmkp.controller.Main',
        'Lmkp.controller.Layers',
        'Lmkp.controller.Map',
        'Lmkp.controller.Filter',
        'Lmkp.controller.EditFilter'
    ],

    //controllers: Lmkp.mainControllers,
    controllers: ['Main', 'Layers', 'Map', 'Filter', 'EditFilter', 'Stakeholder', 'Outer'],
    
    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: {
                type: 'border',
                padding: 0
            },
            items: [{
                // height: 100,
                // region: 'north',
                // xtype: 'header'
                // },{
                region: 'center',
                xtype: 'outerpanel'
            }]
        });
    }
});
