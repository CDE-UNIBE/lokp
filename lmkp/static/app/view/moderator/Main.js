Ext.define('Lmkp.view.moderator.Main' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.main'],

    requires: [
    'Lmkp.view.editor.Map',
    'Lmkp.view.editor.Table',
    'Lmkp.view.moderator.Pending'
    ],

    border: false,
    layout: 'border',

    items: [{
        items: [{
            xtype: 'lo_moderatorpendingpanel'
        },{
            title: 'Table View',
            xtype: 'lo_editortablepanel'
        },{
            title: 'Map View',
            /**
             * collapseMode: 'header' would be much nicer but has some rendering issues:
             * browser window needs to be resized in order to display the collapsed bar properly.
             * Maybe this is a bug in Ext that will be fixed just as:
             * http://www.sencha.com/forum/showthread.php?188414-4.1-RC1-Collapse-mode-mini-doesn-t-work
             */
            // collapseMode: 'header' would be nicer but has some rendering issues
            collapseMode: 'mini', 
            collapsible: true,
            split: true,
            xtype: 'lo_editormappanel'
        }],
        region: 'center',
        xtype: 'tabpanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
});