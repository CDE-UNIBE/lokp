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
        collapsible: false
    },{
        region: 'east',
        width: 500,
        title: 'Map Panel',
        xtype: 'mappanel'
    }],
    
    tbar: [
	'->', {
		xtype: 'combobox',
		fieldLabel: 'Profile',
		id: 'profile_combobox',
		queryMode: 'local',
		store: 'Profiles',
		displayField: 'name',
		valueField: 'profile',
		forceSelection: true
	}, {
		xtype: 'combobox',
		fieldLabel: 'Language',
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