Ext.define('Lmkp.view.administrator.Overview', {
    extend: 'Ext.tab.Panel',
    alias: ['widget.lo_administratorpanel'],

    requires: [
        'Lmkp.view.administrator.YamlScan',
        'Lmkp.view.administrator.UserManagement'
    ],

    items: [
        {
            border: 0,
            frame: false,
            title: 'Activities',
            xtype: 'yamlscanpanel',
            postUrl: '/config/add/activities',
            store: 'YamlScan'
        }, {
            border: 0,
            frame: false,
            title: 'Stakeholders',
            xtype: 'yamlscanpanel',
            postUrl: '/config/add/stakeholders',
            store: 'ShYamlScan'
        }, {
            title: 'Add User',
            xtype: 'lo_usermanagementpanel'
        }
    ]
});