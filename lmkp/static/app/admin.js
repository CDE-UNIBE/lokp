Ext.require('Ext.container.Viewport');
Ext.require('Ext.data.reader.Json');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.CheckboxGroup');
Ext.require('Ext.form.FieldSet');
Ext.require('Ext.form.Hidden');
Ext.require('Ext.form.Label');
Ext.require('Ext.fx.*');
Ext.require('Ext.grid.column.Template');
Ext.require('Ext.grid.Panel');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.layout.container.Column');
Ext.require('Ext.Shadow');
Ext.require('Ext.util.*');
Ext.require('Lmkp.controller.administrator.Code');
Ext.require('Lmkp.controller.administrator.YamlScan');
Ext.require('Lmkp.controller.login.Toolbar');
Ext.require('Lmkp.store.ActivityChangesets');
Ext.require('Lmkp.store.Status');
Ext.require('Lmkp.view.login.Toolbar');
Ext.require('Lmkp.view.users.UserWindow');

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
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'administrator.Code',
        'administrator.YamlScan',
        'login.Toolbar'
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
                    xtype: 'lo_administratorpanel'
                }]
            });
        }
    });
});