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

    commentPanelType: null,

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
            if(this.commentPanelType != null){

                // Activity or Stakeholder?
                var comment_object;
                if (item.modelName == 'Lmkp.model.Activity') {
                    comment_object = 'activity';
                } else if (item.modelName == 'Lmkp.model.Stakeholder') {
                    comment_object = 'stakeholder';
                }

                this.centerPanel.add({
                    comment_object: comment_object,
                    identifier: item.get('id'),
                    xtype: this.commentPanelType
                });
            }
            
        }

        return item;

    }

});