Ext.define('Lmkp.view.administrator.Main', {
    extend: 'Ext.tab.Panel',
	
    alias: ['widget.lo_administratormainpanel'],

    requires: [
    'Lmkp.view.administrator.Home',
    'Lmkp.view.administrator.UserManagement',
    'Lmkp.view.administrator.YamlScan',
    'Lmkp.view.moderator.Pending',
    'Lmkp.view.editor.Overview'
    ],

    activeTab: 0,

    items: [{
        title: 'Pending Changes',
        xtype: 'lo_moderatorpendingpanel'
    },{
        title: 'Overview',
        xtype: 'lo_editoroverviewpanel'
    },{
        postUrl: '/config/add/activities',
        store: 'YamlScan',
        title: 'Activities',
        xtype: 'yamlscanpanel'
    }, {
        postUrl: '/config/add/stakeholders',
        store: 'ShYamlScan',
        title: 'Stakeholders',
        xtype: 'yamlscanpanel'
    },{
        margin: 5,
        title: 'Add User',
        xtype: 'lo_usermanagementpanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
});