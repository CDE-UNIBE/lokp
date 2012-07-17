Ext.onReady(function(){
    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });

    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.administrator.Outer',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'administrator.Main',
        'editor.Table',
        'editor.Detail',
        'login.Toolbar',
        'editor.GxMap',
        'editor.Table',
        'moderator.Pending',
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