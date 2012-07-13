Ext.onReady(function(){
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.administrator.Outer',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'administrator.Main',
        'login.Toolbar',
        'editor.Map',
        'Map',
        'editor.Table',
        'moderator.Pending',
        'Filter',
        'EditFilter',
        'Stakeholder'
        ],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'center',
                    xtype: 'lo_administratorouterpanel'
                }]
            });
        }
    });
});