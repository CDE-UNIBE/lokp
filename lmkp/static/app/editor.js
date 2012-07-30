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