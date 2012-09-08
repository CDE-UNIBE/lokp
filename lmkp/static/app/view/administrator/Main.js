Ext.define('Lmkp.view.administrator.Main', {
    extend: 'Ext.tab.Panel',
    alias: ['widget.lo_administratorpanel'],

    requires: [
    'Lmkp.store.ActivityYamlScan',
    'Lmkp.store.StakeholderYamlScan',
    'Lmkp.view.administrator.CodeTab',
    'Lmkp.view.administrator.UserManagement',
    'Lmkp.view.administrator.YamlScan'
    ],

    frame: false,
    border: 0,

    defaults: {
        border: 0,
        frame: false
    },

    initComponent: function(){

        var stakeholderStore = Ext.create('Lmkp.store.StakeholderYamlScan');
        var activityStore = Ext.create('Lmkp.store.ActivityYamlScan');

        var items = [
        {
            postUrl: '/config/add/activities',
            store: activityStore,
            title: 'Activities',
            xtype: 'lo_administratoryamlscanpanel'
        },{
            postUrl: '/config/add/stakeholders',
            store: stakeholderStore,
            title: 'Stakeholders',
            xtype: 'lo_administratoryamlscanpanel'
        },{
            title: 'Codes',
            xtype: 'lo_administratorcodetab'
        },{
            title: 'Add User',
            xtype: 'lo_usermanagementpanel'
        }];

        this.items = items;

        this.callParent(arguments);
    }
});