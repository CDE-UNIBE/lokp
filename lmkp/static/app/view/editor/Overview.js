//Ext.define('Lmkp.view.editor.Overview' ,{
//    extend: 'Ext.container.Container',
//    alias : ['widget.lo_editoroverviewpanel'],
//
//    requires: [
//        'Lmkp.view.editor.Map',
//        'Lmkp.view.editor.ActivityTable',
//        'Lmkp.view.editor.StakeholderTable'
//    ],
//
//    layout: {
//        type: 'hbox',
//        align: 'stretch'
//    },
//
//    items: [{
//        flex: 0.5,
//        items: [
//            {
//                border: 0,
//                frame: false,
//                title: Lmkp.ts.msg('activities-table_view'),
//                xtype: 'lo_editoractivitytablepanel'
//            }, {
//                border: 0,
//                frame: false,
//                title: Lmkp.ts.msg('stakeholders-table_view'),
//                xtype: 'lo_editorstakeholdertablepanel'
//            }, {
//                border: 0,
//                frame: false,
//                title: Lmkp.ts.msg('map-view'),
//                xtype: 'lo_editormappanel'
//            }
//        ],
//        plain: true,
//        xtype: 'tabpanel'
//    },{
//        flex: 0.5,
//        xtype: 'lo_editordetailpanel'
//    }]
//
//});
