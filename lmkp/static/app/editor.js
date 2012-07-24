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
        'Lmkp.view.editor.Outer',
        ],

        controllers: [
        'activities.NewActivity',
        'login.Toolbar',
        'editor.Detail',
        'editor.Map',
        'editor.Overview',
        'stakeholders.StakeholderFieldContainer',
        'stakeholders.StakeholderSelection'
        ],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    border: 0,
                    frame: false,
                    region: 'center',
                    xtype: 'lo_editorouterpanel'
                }]
            });
        }
    });
});