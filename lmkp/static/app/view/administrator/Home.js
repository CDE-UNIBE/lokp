Ext.define('Lmkp.view.administrator.Home', {
	extend: 'Ext.panel.Panel',
	
	alias: ['widget.adminhomepanel'],
	
	html: 'Welcome to the administration interface.<br/><br/>Here, you can scan the YAML profiles, add their key/value pairs to the database and perform translations.',
	border: 0,
	bodyPadding: 5,
	
	initComponent: function() {
		this.callParent(arguments);
	}
});
