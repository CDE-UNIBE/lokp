Ext.define('Lmkp.view.admin.Main', {
    extend: 'Ext.tab.Panel',
	
    alias: ['widget.adminmainpanel'],

    activeTab: 0,
	
    items: [{
        title: 'Home',
        xtype: 'adminhomepanel'
    }, {
        postUrl: '/config/add/activities',
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