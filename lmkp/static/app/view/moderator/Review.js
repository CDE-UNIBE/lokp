Ext.define('Lmkp.view.moderator.Review', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_moderatorreviewpanel'],
    
    bodyPadding: 5,
    layout: {
        type: 'anchor'
    },
    defaults: {
    	margin: '0 0 5 0',
    	anchor: '100%'
    },
    
    items: [{
        xtype: 'panel',
        name: 'review_initial',
        html: 'Select an item on the left.',
        border: 0
    }],

    updateContentActivity: function(panel, data) {
        console.log(data);
        console.log("Question: 2 functions (Activity / Stakeholder) needed?");

        // remove the initial panel
        if (panel.down('panel[name=review_initial]')) {
            panel.remove(panel.down('panel[name=review_initial]'));
        }

        // remove existing review panel (activity)
        while (panel.down('panel[name=review_activity]')) {
            panel.remove(panel.down('panel[name=review_activity]'));
        }

        for (var i in data.data) {
            if (data.data[i].status == 'pending') {
                var newPanel = Ext.create('Ext.panel.Panel', {
                    name: 'review_activity',
                    html: data.data[i].source
                });
                panel.add(newPanel);
            }
        }
    },

    updateContentStakeholder: function(panel, data) {
        console.log(data);
        console.log("coming soon");
        console.log("Question: 2 functions (Activity / Stakeholder) needed?");
    }
});