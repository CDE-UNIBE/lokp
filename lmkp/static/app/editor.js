Ext.onReady(function(){
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.editor.Outer',
        ],

        //controllers: ['Main', 'Layers', 'Map', 'Filter', 'EditFilter', 'Stakeholder', 'Outer'],
        controllers: ['login.Toolbar'],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'center',
                    xtype: 'lo_editorouterpanel'
                }]
            });
        }
    });
});