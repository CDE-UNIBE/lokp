Ext.require('Ext.container.Viewport');


Ext.onReady(function() {
    // Initialize and launch application
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
            'Lmkp.view.login.Toolbar',
            'Lmkp.view.translation.Main'
        ],

        controllers: [
            'login.Toolbar'
        ],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                border: false,
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [
                    {
                        region: 'north',
                        xtype: 'lo_logintoolbar'
                    }, {
                        autoScroll: true,
                        contentEl: 'header-div',
                        region: 'north',
                        xtype: 'panel'
                    }, {
                        region: 'center',
                        xtype: 'lo_translationpanel'
                    }
                ]
            });

            // Remove loading mask
            var loadingMask = Ext.get('loading-mask');
            loadingMask.fadeOut({
                duration: 1000,
                remove: true
            });
        }
    });
});