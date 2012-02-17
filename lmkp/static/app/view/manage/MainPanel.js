Ext.define('Lmkp.view.manage.MainPanel',{
    extend: 'Ext.panel.Panel',

    alias: ['widget.managemainpanel'],

    items: [{
        items: [{
            title: 'Activities',
            xtype: 'manageactivitiestreepanel'
        },{
            title: 'Stakeholders',
            xtype: 'panel'
        }],
        region: 'west',
        resizable: true,
        width: 200,
        xtype: 'tabpanel'
    },{
        id: 'activity-details-panel',
        region: 'center',
        xtype: 'manageactivitiesdetails'
    },{
        collapsible: true,
        html: 'wannabe map panel',
        region: 'east',
        width: 100,
        xtype: 'panel'
    }],

    layout: 'border',

    tbar: [{
        menu: {
            items: [{
                text: 'regular item 1'
            },{
                text: 'regular item 2'
            },{
                text: 'regular item 3'
            }],
            xtype: 'menu'
        },
        text: 'File',
        xtype: 'button'
    },{
        menu: {
            items: [{
                text: 'regular item 1'
            },{
                text: 'regular item 2'
            },{
                text: 'regular item 3'
            }],
            xtype: 'menu'
        },
        text: 'View',
        xtype: 'button'
    }],

    initComponent: function(){
        //console.log('Lmkp.view.manage.MainPanel: initComponent');
        this.callParent(arguments);
    }
});