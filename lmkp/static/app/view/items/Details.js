/**
 * Super class for Lmkp.view.activities.Details and
 * Lmkp.view.stakeholders.Details.
 */
Ext.define('Lmkp.view.items.Details',{
    extend: 'Ext.window.Window',

    bbar: {
        items: ['->', {
            iconCls: 'cancel-button',
            itemId: 'closeWindowButton',
            scale: 'medium',
            text: 'Close', // also translate tooltip
            tooltip: Lmkp.ts.msg('Close window')
        }],
        xtype: 'toolbar'
    },

    bodyPadding: 5,

    centerPanelType: null,

    defaults: {
        margin: '0 0 5 0',
        anchor: '100%'
    },

    height: 500,

    layout: 'border',

    modal: true,

    width: 700,

    /**
     * Ext has some serious issues with panels collapsed on start. Instead, this
     * function is called right after showing this window.
     */
    _collapseHistoryPanel: function() {
        if (this.historyPanel) {
            this.historyPanel.collapse();
        }

        return this;
    },


    /**
     * Parameter stakeholder is an instance of Lmkp.model.Stakeholder
     */
    _populateDetails: function(item){

        if (item) {

            // Set the current selection to current
            this.current = item;

            // Remove all existing panels
            this.centerPanel.removeAll();

            // Show a notice with the current status of this version
            if(item.get('status') == 'pending') {
                this.centerPanel.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing a <b>pending</b> version, which needs to be \n\
                        reviewed before it is publicly visible.',
                    margin: '3 3 0 3'

                });
            } else if(item.get('status') == 'inactive') {
                this.centerPanel.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing an <b>inactive</b> version, which was previously active.',
                    margin: '3 3 0 3'

                });
            } else if(item.get('status') == 'deleted') {
                this.centerPanel.add({
                    bodyCls: 'warning',
                    bodyPadding: 5,
                    html: 'You are seeing a <b>deleted</b> version.',
                    margin: '3 3 0 3'

                });
            } else if(item.get('status') == 'rejected') {
                this.centerPanel.add({
                    bodyCls: 'warning',
                    bodyPadding: 5,
                    html: 'You are seeing a <b>rejected</b> version.',
                    margin: '3 3 0 3'

                });
            } else if(item.get('status') == 'edited') {
                this.centerPanel.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing an <b>edited</b> version.',
                    margin: '3 3 0 3'

                });
            }

            // If there are no versions pending, simply show active version
            this.centerPanel.add({
                contentItem: item,
                border: 0,
                bodyPadding: 0,
                editable: true,
                hiddenOriginal: false,
                xtype: this.centerPanelType
            });

            // Add commenting panel
            this.centerPanel.add({
                comment_object: 'stakeholder',
                identifier: item.get('id'),
                xtype: 'lo_commentpanel'
            });
        }

        return item;

    }

});