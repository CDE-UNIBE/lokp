Ext.define('Lmkp.view.Main' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.main'],
    
    layout: 'border',
    defaults: {
        collapsible: true,
        split: true
    },

    items : [{
        region: 'center',
        xtype: 'sidepanel',
        collapsible: false,
        width: 300
    },{
        region: 'east',
        width: 500,
        title: 'Map Panel',
        xtype: 'mappanel'
    }],
    
    tbar: [
	'->', {
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

    initComponent: function() {
        this.callParent(arguments);
    }
});