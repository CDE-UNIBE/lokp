Ext.define('Lmkp.view.Main' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.main'],
    
    layout: 'border',

    items : [{
        region: 'center',
        xtype: 'sidepanel',
    },{
        region: 'east',
        width: 500,
        title: 'Map',
        xtype: 'mappanel',
        /**
         * collapseMode: 'header' would be much nicer but has some rendering issues:
         * browser window needs to be resized in order to display the collapsed bar properly.
         * Maybe this is a bug in Ext that will be fixed just as:
         * http://www.sencha.com/forum/showthread.php?188414-4.1-RC1-Collapse-mode-mini-doesn-t-work
         */
        // collapseMode: 'header' would be nicer but has some rendering issues
        collapseMode: 'mini', 
        collapsible: true,
        split: true
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