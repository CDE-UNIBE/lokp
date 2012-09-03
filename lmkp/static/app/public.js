Ext.require('Ext.container.Viewport');
Ext.require('Ext.form.action.StandardSubmit');
Ext.require('Ext.form.field.Checkbox');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.field.Hidden');
Ext.require('Ext.form.Panel');
Ext.require('Ext.fx.*');
Ext.require('Ext.grid.Panel');
Ext.require('Ext.layout.container.Border');
Ext.require('Lmkp.utils.StringFunctions');
Ext.require('Lmkp.view.activities.Details');
Ext.require('Lmkp.view.comments.ReCaptcha');

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
        'Lmkp.view.login.Toolbar',
        'Lmkp.view.public.Main'
        ],

        controllers: [
        'activities.Details',
        'login.Toolbar',
        'public.Main',
        'public.BaseLayers',
        'public.ContextLayers',
        'stakeholders.Details',
        'public.Filter',
        'public.Map'
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
                    contentEl: 'header-div',
                    height: 80,
                    region: 'north',
                    xtype: 'panel'
                },{
                    region: 'center',
                    xtype: 'lo_publicmainpanel'
                }]
            });
        }
    });
});