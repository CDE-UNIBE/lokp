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
    },/*{
        collapsible: true,
        html: 'wannabe map panel',
        region: 'east',
        width: 100,
        xtype: 'panel'
    }*/Ext.create('Lmkp.view.MapPanel',{
        region: 'east',
        resizable: true,
        width: 600
    })],

    layout: 'border',

    tbar: [{
        menu: {
            items: [{
                text: 'regular item 1'
            },{
                text: 'regular item 2'
            },{
                text: 'regular item 3'
            }, {
            	text: 'configuration',
            	id: 'menubutton_config'
            }],
            xtype: 'menu'
        },
        text: Lmkp.ts.msg("file-menu"),
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
        text: Lmkp.ts.msg("view-menu"),
        xtype: 'button'
    },'->',{
        fieldLabel: 'Choose country',
        id: 'locale-combobox',
        queryMode: 'local',
        store: [['de', 'Germany'],['de_CH', 'Switzerland'],['lo_LA', 'Laos'],['fr','France']],
        xtype: 'combo'
    }],

    initComponent: function(){
        //console.log('Lmkp.view.manage.MainPanel: initComponent');
        this.callParent(arguments);
    }
});