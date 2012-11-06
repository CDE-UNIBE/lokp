/**
 * Super class for Lmkp.view.activities.Details and
 * Lmkp.view.stakeholders.Details.
 */
Ext.define('Lmkp.view.items.Details',{
    extend: 'Ext.window.Window',
    alias: ['widget.lo_itemdetailwindow'],

    bbar: {
        items: ['->', {
            iconCls: 'cancel-button',
            itemId: 'closeWindowButton',
            scale: 'medium',
            text: Lmkp.ts.msg('button_close'),
            tooltip: Lmkp.ts.msg('tooltip_close-window')
        }],
        xtype: 'toolbar'
    },

    bodyPadding: 5,

    centerPanelType: null,

    config: {
        /**
         * XType of the comment panel that will be inserted.
         */
        commentPanelType: null,
        /**
         * A comment object for this item (activity resp. stakeholder). The object
         * is the result from a /comments/activity/{id} resp.
         * /comments/stakeholder/{id} request.
         */
        itemComment: null
    },

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

            this._populateComment(item);
            
        }

        return item;

    },

    _populateComment: function(item){

        // First check if there is already an existing comment panel and remove
        // it if yes.
        var cp = this.centerPanel.down(this.commentPanelType + '[itemId="panelcommentPanel"]');
        if(cp){
            this.centerPanel.remove(cp);
        }

        // Add commenting panel
        if(this.commentPanelType != null && this.itemComment != null){

            // Activity or Stakeholder?
            var commentType;
            if (item.modelName == 'Lmkp.model.Activity') {
                commentType = 'activity';
            } else if (item.modelName == 'Lmkp.model.Stakeholder') {
                commentType = 'stakeholder';
            }

            var commentPanel = this.centerPanel.add({
                commentType: commentType,
                commentsObject: this.itemComment,
                itemId: 'commentPanel',
                identifier: item.get('id'),
                margin: 3,
                xtype: this.commentPanelType
            });
            commentPanel._redoLayout();
        }
    }

});