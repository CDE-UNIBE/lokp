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
                tbar: [Lmkp.login_form
                ,'->', {
                    xtype: 'combobox',
                    fieldLabel: Lmkp.ts.msg("profile-label"),
                    labelAlign: 'right',
                    id: 'profile_combobox',
                    queryMode: 'local',
                    store: 'Profiles',
                    displayField: 'name',
                    valueField: 'profile',
                    forceSelection: true
                }, {
                    xtype: 'combobox',
                    fieldLabel: Lmkp.ts.msg("language-label"),
                    labelAlign: 'right',
                    id: 'language_combobox',
                    queryMode: 'local',
                    store: 'Languages',
                    displayField: 'english_name',
                    valueField: 'locale',
                    forceSelection: true
                }],
                xtype: 'panel'
            }],

            tbar: [Lmkp.login_form]
        });
    }
});
