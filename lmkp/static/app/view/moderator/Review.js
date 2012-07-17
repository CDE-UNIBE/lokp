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

    updateContentActivity: function(data) {

        // Remove any existing panels
        this.removeAll();

        // Add a panel for each Activity
        for (p in data.data) {
            var p = Ext.create('Lmkp.view.activities.ActivityPanel', {
                activity: data.data[p]
            });
            this.add(p);
        }
    },

    updateContentStakeholder: function(panel, data) {
        console.log(data);
        console.log("coming soon");
        console.log("Question: 2 functions (Activity / Stakeholder) needed?");
    }
});