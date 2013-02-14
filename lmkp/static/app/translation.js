Ext.require('Ext.container.Viewport');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.Panel');
Ext.require('Ext.grid.column.Template');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.layout.component.field.ComboBox');
Ext.require('Lmkp.controller.login.Toolbar');
Ext.require('Lmkp.controller.translation.KeyValues');
Ext.require('Lmkp.store.ActivityYamlScan');
Ext.require('Lmkp.store.StakeholderYamlScan');
Ext.require('Lmkp.utils.MessageBox');
Ext.require('Lmkp.view.translation.Main');

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
            'login.Toolbar',
            'translation.KeyValues'
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
                        xtype: 'lo_logintoolbar',
                        hideProfileSelection: true
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
