Ext.require('Ext.container.Viewport');

Ext.onReady(function() {

    var appFolder = openItem == 'true' ? '../../static/app' : 'static/app';

    // Initialize and launch application
    Ext.application({
        name: 'Lmkp',
        appFolder: appFolder,

        requires: [
            'Lmkp.view.login.Toolbar'
        ],

        controllers: [
            'login.Toolbar',
            'moderation.Main',
            'moderation.Pending',
            'moderation.CompareReview',
            'activities.NewActivity',
            'stakeholders.NewStakeholder'
        ],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                border: false,
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'north',
                    xtype: 'lo_logintoolbar'
                },{
                    autoScroll: true,
                    contentEl: 'header-div',
                    height: 105,
                    region: 'north',
                    xtype: 'panel'
                },{
                    region: 'center',
                    xtype: 'lo_moderationpanel'
                }]
            });

            if (type && identifier) {
                // Try to set pending tab active
                var tabpanel = Ext.ComponentQuery.query('lo_moderationpanel')[0];
                if (tabpanel) {
                    tabpanel.setActiveTab('pendingtab');
                }
                // Show popup with comparison of the requested object
                var controller = this.getController('moderation.Pending');
                controller.onCompareButtonClick({
                    type: type,
                    identifier: identifier
                });
            }

            // Remove loading mask
            var loadingMask = Ext.get('loading-mask');
            loadingMask.fadeOut({
                duration: 1000,
                remove: true
            });
        }
    });
});