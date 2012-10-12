//Ext.define('Lmkp.view.activities.History', {
//    extend: 'Ext.panel.Panel',
//    alias: ['widget.lo_activityhistorypanel'],
//
//    itemId: 'activityHistoryPanel',
//
//    bodyPadding: 5,
//
//    layout: {
//        type:'vbox',
//        align:'stretch'
//    },
//    defaults: {
//        margins:'0 0 5 0',
//        bodyPadding: 5
//    },
//
//    // initial item
//    items: [{
//        xtype: 'panel',
//        border: 0,
//        name: 'history_initial',
//        html: 'Select an activity above to show its history',
//        collapsible: false,
//        collapsed: false
//    }],
//
//    updateContent: function(data, types) {
//        if (data) {
//            // Activity or Stakeholder?
//            var xtype = null;
//            if (types == 'activities') {
//                xtype = 'lo_activitypanel';
//            } else if (types == 'stakeholders') {
//                xtype = 'lo_stakeholderpanel';
//            }
//
//            // Remove any existing panels
//            this.removeAll();
//
//            var panels = [];
//            for (var i in data.data) {
//                var first = (i == 0);
//                var p = Ext.create('Lmkp.view.activities.ChangesetPanel', {
//                    // Panel data
//                    timestamp: data.data[i].timestamp,
//                    version: data.data[i].version,
//                    previous_version: data.data[i].previous_version,
//                    username: data.data[i].username,
//                    userid: data.data[i].userid,
//                    additionalPanelBottom: {
//                        xtype: xtype,
//                        contentItem: data.data[i],
//                        border: 0,
//                        editable: false
//                    },
//                    // Panel settings
//                    title: Lmkp.ts.msg('version') + ' ' + data.data[i].version,
//                    collapsible: true,
//                    collapsed: !first // all except first are collapsed
//
//                });
//                panels.push(p);
//            }
//            this.add(panels);
//        }
//    }
//});
