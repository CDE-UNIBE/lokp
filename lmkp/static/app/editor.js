Ext.require('Ext.container.Viewport');
Ext.require('Ext.data.reader.Json');
Ext.require('Ext.form.action.StandardSubmit');
Ext.require('Ext.form.field.Checkbox');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.FieldSet');
Ext.require('Ext.form.Hidden');
Ext.require('Ext.form.Label');
Ext.require('Ext.form.Panel');
Ext.require('Ext.fx.*');
Ext.require('Ext.grid.column.Template');
Ext.require('Ext.grid.Panel');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.layout.container.Column');
Ext.require('Lmkp.utils.StringFunctions');
Ext.require('Lmkp.store.ActivityChangesets');
Ext.require('Lmkp.store.Status');
Ext.require('Lmkp.view.comments.ReCaptcha');
Ext.require('Lmkp.view.activities.ChangesetPanel');
Ext.require('Lmkp.view.stakeholders.StakeholderPanel');
Ext.require('Lmkp.view.users.ChangePasswordWindow');
Ext.require('Lmkp.view.users.UserWindow');

Ext.onReady(function(){

    /**
     * This is probably not needed anymore!
     */
    console.log("Don't delete me!!!");

    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });
    
    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.editor.Overview',
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'activities.NewActivity',
        'activities.TagGroup',
        'login.Toolbar',
        'editor.BaseLayers',
        'editor.ContextLayers',
        'editor.Detail',
        'editor.Map',
        'editor.Overview',
        'stakeholders.NewStakeholder',
        'stakeholders.StakeholderFieldContainer',
        'stakeholders.StakeholderSelection'
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
                    border: 0,
                    frame: false,
                    region: 'center',
                    xtype: 'lo_editoroverviewpanel'
                }]
            });
        }
    });
});