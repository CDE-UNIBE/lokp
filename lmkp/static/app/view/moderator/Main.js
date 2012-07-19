Ext.define('Lmkp.view.moderator.Main' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_moderatormainpanel'],

    requires: [
    'Lmkp.view.editor.Overview',
    'Lmkp.view.moderator.Pending'
    ],

    border: false,
    layout: 'border',

    items: [{
        items: [{
            title: 'Pending Changes',
            xtype: 'lo_moderatorpendingpanel'
        },{
            title: 'Overview',
            xtype: 'lo_editoroverviewpanel'
        }],
        region: 'center',
        xtype: 'lo_tabpanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
});