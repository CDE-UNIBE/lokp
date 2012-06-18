Ext.define('Lmkp.view.admin.MainPanel', {
    extend: 'Ext.tab.Panel',
	
    alias: ['widget.adminmainpanel'],
	
    activeTab: 0,
	
    items: [{
        title: 'Home',
        xtype: 'adminhome'
    }, {
        title: 'Activities',
        xtype: 'adminyamlscan'
    }, {
        title: 'Stakeholders',
        xtype: 'shadminyamlscan'
    }],
	
    initComponent: function() {
        this.callParent(arguments);
    }
});