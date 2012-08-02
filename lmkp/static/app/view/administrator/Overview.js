Ext.define('Lmkp.view.administrator.Overview', {
    extend: 'Ext.tab.Panel',
    alias: ['widget.lo_administratorpanel'],

    requires: [
        'Lmkp.view.administrator.YamlScan',
        'Lmkp.view.administrator.UserManagement'
    ],

    frame: false,
    border: 0,

    defaults: {
        border: 0,
        frame: false
    },

    items: [
        {
            title: 'Activities',
            xtype: 'yamlscanpanel',
            postUrl: '/config/add/activities',
            store: 'YamlScan'
        }, {
            title: 'Stakeholders',
            xtype: 'yamlscanpanel',
            postUrl: '/config/add/stakeholders',
            store: 'ShYamlScan'
        }, {
            title: 'Codes',
            xtype: 'lo_administratorcodetab'
        }, {
            title: 'Add User',
            xtype: 'lo_usermanagementpanel'
        }
    ]
});