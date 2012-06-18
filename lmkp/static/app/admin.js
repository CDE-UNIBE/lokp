Ext.application({
    name: 'Lmkp',
    appFolder: 'static/app',
	
    controllers: [
    'admin.Main'
    ],
	
    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [{
                id: 'outer-panel',
                items: [{
                    region: 'center',
                    xtype: 'adminmainpanel'
                }],
                layout: 'border',
                region: 'center',
                tbar: [Lmkp.login_form],
                xtype: 'panel'
            }],

            tbar: [Lmkp.login_form]
        });
    }
});
