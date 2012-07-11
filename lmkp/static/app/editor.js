Ext.onReady(function(){
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

        controllers: ['Main', 'Layers', 'Map', 'Filter', 'EditFilter', 'Stakeholder', 'Outer'],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'center',
                    xtype: 'lo_editorpanel'
                }]
            });
        }
    });
});