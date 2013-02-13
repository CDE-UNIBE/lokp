Ext.define('Lmkp.view.translation.Main', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.lo_translationpanel',

    requires: [
        'Lmkp.view.translation.OverviewTab',
        'Lmkp.view.translation.KeyValueTree'
    ],

    frame: false,
    border: 0,
    defaults: {
        border: 0,
        frame: false,
        bodyPadding: 5
    },

    initComponent: function() {

        // Create and load stores
        var aStore = Ext.create('Lmkp.store.ActivityYamlScan');
        var shStore = Ext.create('Lmkp.store.StakeholderYamlScan');

        var items = [
            {
                xtype: 'lo_translationoverviewtab'
            }, {
                xtype: 'lo_translationkeyvaluetree',
                title: 'Activities',
                store: aStore,
                postUrl: '/config/add/activities'
            }, {
                xtype: 'lo_translationkeyvaluetree',
                title: 'Stakeholders',
                store: shStore,
                postUrl: '/config/add/stakeholders'
            }
        ];

        this.items = items;

        this.callParent(arguments);
    }

});