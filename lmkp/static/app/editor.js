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
        'login.Toolbar',
        'editor.Detail',
        'editor.Overview',
        'Stakeholder',
        'stakeholders.StakeholderFieldContainer'
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