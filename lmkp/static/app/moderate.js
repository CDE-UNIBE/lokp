Ext.require('Ext.container.Viewport');
Ext.require('Ext.form.action.Action');
Ext.require('Ext.form.action.Load');
Ext.require('Ext.form.action.Submit');
Ext.require('Ext.form.FieldSet');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.field.Date');
Ext.require('Ext.form.field.Display');
Ext.require('Ext.form.field.Hidden');
Ext.require('Ext.form.field.Number');
Ext.require('Ext.form.field.Picker');
Ext.require('Ext.form.field.TextArea');
Ext.require('Ext.form.Basic');
Ext.require('Ext.form.Label');
Ext.require('Ext.form.Panel');
Ext.require('Ext.grid.column.Template');
Ext.require('Ext.grid.Panel');
Ext.require('Ext.layout.container.Anchor');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.layout.component.BoundList');
Ext.require('Ext.layout.component.ProgressBar');
Ext.require('Ext.layout.component.field.ComboBox');
Ext.require('Ext.layout.component.field.TextArea');
Ext.require('Ext.resizer.BorderSplitter');
Ext.require('Ext.resizer.Splitter');
Ext.require('Ext.resizer.SplitterTracker');
Ext.require('Ext.ProgressBar');
Ext.require('Ext.toolbar.Paging');
Ext.require('Ext.view.BoundList');
Ext.require('Ext.view.BoundListKeyNav');
Ext.require('Ext.window.MessageBox');
Ext.require('Lmkp.controller.activities.NewActivity');
Ext.require('Lmkp.controller.login.Toolbar');
Ext.require('Lmkp.controller.moderation.Pending');
Ext.require('Lmkp.controller.moderation.CompareReview');
Ext.require('Lmkp.controller.stakeholders.NewStakeholder');
Ext.require('Lmkp.store.ActivityChangesets');
Ext.require('Lmkp.store.Status');
Ext.require('Lmkp.utils.MessageBox');
Ext.require('Lmkp.utils.PermalinkWindow');
Ext.require('Lmkp.utils.StringFunctions');
Ext.require('Lmkp.view.login.Toolbar');
Ext.require('Lmkp.view.moderation.Main');
Ext.require('Lmkp.view.stakeholders.NewStakeholderSelection');
Ext.require('Lmkp.view.users.ChangePasswordWindow');
Ext.require('Lmkp.view.users.UserWindow');

Ext.onReady(function() {

    var appFolder = openItem == 'true' ? '../../static/app' : 'static/app';

    // Initialize and launch application
    Ext.application({
        name: 'Lmkp',
        appFolder: appFolder,

        requires: [
            'Lmkp.view.login.Toolbar',
            'Lmkp.view.moderation.Main'
        ],

        controllers: [
        'login.Toolbar',
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