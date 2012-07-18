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

        var previous_version = []
        // First add a panel for each with status 'pending'
        for (var i in data.data) {
            if (data.data[i].status == 'pending') {
                this.add(
                    Ext.create('Lmkp.view.activities.ChangesetPanel', {
                        // Panel data
                        timestamp: data.data[i].timestamp,
                        version: data.data[i].version,
                        previous_version: data.data[i].previous_version,
                        username: data.data[i].username,
                        userid: data.data[i].userid,
                        additionalPanelBottom: Ext.create(
                            'Lmkp.view.activities.ActivityPanel', {
                                activity: data.data[i],
                                border: 0
                            }
                        ),
                        // Panel settings
                        title: 'Pending version',
                        collapsible: true
                    })
                );
                // Add its previous version to list
                previous_version.push(data.data[i].previous_version);
            }
        }
        // Then loop again to add their previous versions
        for (var j in data.data) {
            for (var pv in previous_version) {
                if (data.data[j].version == previous_version[pv]) {
                    this.add(
                        Ext.create('Lmkp.view.activities.ChangesetPanel', {
                            // Panel data
                            timestamp: data.data[j].timestamp,
                            version: data.data[j].version,
                            previous_version: data.data[j].previous_version,
                            username: data.data[j].username,
                            userid: data.data[j].userid,
                            additionalPanelBottom: Ext.create(
                                'Lmkp.view.activities.ActivityPanel', {
                                    activity: data.data[j],
                                    border: 0
                                }
                            ),
                            // Panel settings
                            title: 'Previous version',
                            collapsible: true,
                            collapsed: true
                        })
                    );
                }
            }
        }
    },

    updateContentStakeholder: function(data) {
        console.log(data);
        console.log("coming soon");
        console.log("Question: 2 functions (Activity / Stakeholder) needed?");
    }
});