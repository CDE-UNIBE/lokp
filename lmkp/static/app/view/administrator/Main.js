Ext.define('Lmkp.view.administrator.Main', {
    extend: 'Ext.tab.Panel',
	
    alias: ['widget.lo_administratormainpanel'],

    requires: [
    'Lmkp.view.administrator.Home',
    'Lmkp.view.administrator.YamlScan',
    'Lmkp.view.moderator.Pending',
    'Lmkp.view.editor.Table',
    'Lmkp.view.editor.Map'
    ],

    activeTab: 0,

    items: [{
        title: 'Pending Changes',
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
    },{
        postUrl: '/config/add',
        store: 'YamlScan',
        title: 'Activities',
        xtype: 'yamlscanpanel'
    }, {
        postUrl: '/config/add/stakeholders',
        store: 'ShYamlScan',
        title: 'Stakeholders',
        xtype: 'yamlscanpanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
});