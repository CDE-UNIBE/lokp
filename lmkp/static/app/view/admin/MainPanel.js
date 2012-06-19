Ext.define('Lmkp.view.admin.MainPanel', {
    extend: 'Ext.tab.Panel',
	
    alias: ['widget.adminmainpanel'],

    activeTab: 0,
	
    items: [{
        title: 'Home',
        xtype: 'adminhome'
    }, {
        postUrl: '/config/add',
        store: 'YamlScan',
        title: 'Activities',
        xtype: 'yamlscanpanel'
    }, {
        postUrl: '/config/add/stakeholders',
        store: 'ShYamlScan',
        title: 'Stakeholders',
        xtype: 'yamlscanpanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
});