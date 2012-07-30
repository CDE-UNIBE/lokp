Ext.define('Lmkp.view.administrator.Main', {
    extend: 'Ext.tab.Panel',
	
    alias: ['widget.lo_administratormainpanel'],

    requires: [
    'Lmkp.view.moderator.Pending',
    'Lmkp.view.editor.Overview',
    'Lmkp.view.administrator.Overview'
    ],

    activeTab: 0,

    items: [{
        title: 'Pending Changes',
        xtype: 'lo_moderatorpendingpanel'
    },{
        title: 'Overview',
        xtype: 'lo_editoroverviewpanel'
    }, {
        title: 'Administration',
        xtype: 'lo_administratorpanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
});