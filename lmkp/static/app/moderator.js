Ext.onReady(function(){
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.moderator.Outer',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'login.Toolbar',
        'editor.Map',
        'Map',
        'editor.Table',
        'moderator.Pending',
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
                    xtype: 'lo_moderatorouterpanel'
                }]
            });
        }
    });
});