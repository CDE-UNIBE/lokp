Ext.define('Lmkp.view.Main' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.main'],

    border: false,
    layout: 'border',

    items: [{
        items: [{
            xtype: 'pendingpanel'
        },{
            xtype: 'lo_tablepanel'
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
            xtype: 'mappanel'
        }],
        region: 'center',
        xtype: 'tabpanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
});