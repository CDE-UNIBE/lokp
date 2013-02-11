Ext.require('Ext.container.Viewport');
Ext.require('Ext.form.action.StandardSubmit');
Ext.require('Ext.form.FieldSet');
Ext.require('Ext.form.field.Checkbox');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.field.Hidden');
Ext.require('Ext.form.Label');
Ext.require('Ext.form.Panel');
Ext.require('Ext.fx.*');
Ext.require('Ext.grid.Panel');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.layout.container.Card');
Ext.require('Ext.tab.Panel');
Ext.require('Ext.util.*');
Ext.require('GeoExt.window.Popup');
Ext.require('Lmkp.controller.activities.Details');
Ext.require('Lmkp.controller.activities.NewActivity');
Ext.require('Lmkp.controller.editor.Map');
Ext.require('Lmkp.controller.login.Toolbar');
Ext.require('Lmkp.controller.moderator.Details');
Ext.require('Lmkp.controller.moderator.Main');
Ext.require('Lmkp.controller.public.BaseLayers');
Ext.require('Lmkp.controller.public.ContextLayers');
Ext.require('Lmkp.controller.public.Filter');
Ext.require('Lmkp.controller.public.Main');
Ext.require('Lmkp.controller.public.Map');
Ext.require('Lmkp.controller.moderation.CompareReview');
Ext.require('Lmkp.controller.stakeholders.Details');
Ext.require('Lmkp.controller.stakeholders.NewStakeholder');
Ext.require('Lmkp.store.ActivityChangesets');
Ext.require('Lmkp.store.ReviewDecisions');
Ext.require('Lmkp.store.Status');
Ext.require('Lmkp.utils.StringFunctions');
Ext.require('Lmkp.view.activities.Details');
Ext.require('Lmkp.view.comments.ReCaptcha');
Ext.require('Lmkp.view.login.Toolbar');
Ext.require('Lmkp.view.public.Main');
Ext.require('Lmkp.view.users.UserWindow');
Ext.require('Lmkp.view.stakeholders.NewStakeholderSelection');
Ext.require('Lmkp.utils.MessageBox');

Ext.onReady(function(){
    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });
    
    // Collect additional controllers (based on login permissions, eg. see 
    // function 'edit_toolbar_config' in 'views/editors.py')
    var additionalControllers = [];
    if (Lmkp.editorControllers) {
        additionalControllers = additionalControllers.concat(Lmkp.editorControllers);
    }
    if(Lmkp.moderatorControllers) {
        additionalControllers = additionalControllers.concat(Lmkp.moderatorControllers);
    }

    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Ext.container.Viewport',
        'Lmkp.controller.activities.Details',
        'Lmkp.controller.login.Toolbar',
        'Lmkp.controller.public.Main',
        'Lmkp.controller.public.BaseLayers',
        'Lmkp.controller.public.ContextLayers',
        'Lmkp.controller.stakeholders.Details',
        'Lmkp.controller.public.Filter',
        'Lmkp.controller.public.Map',
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
        'public.Map',
        ].concat(additionalControllers),

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
                    height: 112, // 100 + 2x border + 10px padding
                    // Hide the header panel if the Land Observatory is embedded
                    hidden: Lmkp.is_embedded,
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