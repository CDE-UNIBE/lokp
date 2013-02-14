Ext.define('Lmkp.view.administrator.Main', {
    extend: 'Ext.tab.Panel',
    alias: ['widget.lo_administratorpanel'],

    requires: [
        'Lmkp.store.ActivityYamlScan',
        'Lmkp.store.StakeholderYamlScan',
        'Lmkp.view.administrator.CodeTab',
        'Lmkp.view.administrator.UserManagement',
        'Lmkp.view.administrator.YamlScan',
        'Lmkp.view.administrator.OverviewTab'
    ],

    frame: false,
    border: 0,
    defaults: {
        border: 0,
        frame: false
    },

    initComponent: function(){

        // Create and load stores
        var stakeholderStore = Ext.create('Lmkp.store.StakeholderYamlScan');
        var activityStore = Ext.create('Lmkp.store.ActivityYamlScan');

        var items = [
            {
                xtype: 'lo_administratoroverviewtab'
            }, {
                xtype: 'lo_administratoryamlscanpanel',
                title: Lmkp.ts.msg('activities_attributes'),
                type: 'activity',
                store: activityStore
            }, {
                xtype: 'lo_administratoryamlscanpanel',
                title: Lmkp.ts.msg('stakeholders_attributes'),
                type: 'stakeholder',
                store: stakeholderStore
            }, {
                title: Lmkp.ts.msg('administration_batch-translation'),
                xtype: 'lo_administratorcodetab'
            }, {
                title: Lmkp.ts.msg('administration_profiles'),
                xtype: 'panel',
                html: 'Add (remove?) profiles'
            }, {
                title: Lmkp.ts.msg('administration_user-management'),
                xtype: 'lo_usermanagementpanel'
            }
        ];

        this.items = items;

        this.callParent(arguments);
    }
});