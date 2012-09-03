Ext.define('Lmkp.view.activities.Details', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_activitydetailwindow'],
    
    bodyPadding: 5,
    
    config: {
        centerPanel: null,
        historyPanel: null
    },
    
    defaults: {
        margin: '0 0 5 0',
        anchor: '100%'
    },

    itemId: 'activityDetailWindow',

    height: 600,

    layout: {
        type: 'border'
    },

    requires: [
    'Lmkp.view.activities.ActivityPanel',
    'Lmkp.view.comments.CommentPanel'
    ],

    tbar: {
        dock: 'top',
        xtype: 'toolbar',
        items: [/*{
            enableToggle: true,
            itemId: 'show-all-details',
            pressed: true,
            scale: 'medium',
            text: Lmkp.ts.msg('details-toggle_all')
        },*/{
            iconCls: 'add-info-button',
            itemId: 'add-taggroup-button',
            scale: 'medium',
            text: 'Add further information',
            tooltip: Lmkp.ts.msg('activities-add_further_information')
        }, '->', {
            // @TODO: Add an iconCls
            iconCls: 'delete-button',
            text: 'Delete', // also translate tooltip
            scale: 'medium',
            itemId: 'delete-item-button',
            tooltip: 'to be translated'
        }]
    },

    width: 800,

    initComponent: function(){

        this.centerPanel = Ext.create('Ext.panel.Panel',{
            defaults: {
                margin: '0 0 5 0',
                anchor: '100%'
            },
            region: 'center',
            layout: 'anchor'
        });

        this.historyPanel = Ext.create('Ext.panel')

        this._populateDetails(this.activity)

        var items = [this.centerPanel];

        this.items = items;

        this.callParent(arguments);
    },

    /**
     * Parameter activity is an instance of Lmkp.model.Activity
     */
    _populateDetails: function(activity){

        if (activity) {

            // Set the current selection to current
            this.current = activity;

            // Remove all existing panels
            this.centerPanel.removeAll();

            // If there are no versions pending, simply show active version
            this.centerPanel.add({
                contentItem: activity,
                border: 0,
                bodyPadding: 0,
                editable: false,
                hiddenOriginal: false,
                xtype: 'lo_activitypanel'
            });

            // Add commenting panel
            this.centerPanel.add({
                xtype: 'lo_commentpanel',
                identifier: activity.get('id'),
                comment_object: 'activity'
            });
            
        }

        return activity;

    }
	
});
