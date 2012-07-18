Ext.define('Lmkp.view.activities.TagGroupPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.lo_taggrouppanel',
	
    layout: 'anchor',
    defaults: {
        anchor: '100%'
    },
    bodyPadding: 5,

    items: [{
        border: 0,
        name: 'maintagpanel'
    }, {
        border: 0,
        name: 'tagspanel'
    }],
	
    initComponent: function() {
        var me = this;

        // call parent first
        this.callParent(arguments);

        // main tag
        if (me.main_tag) {
            this._getMainTagPanel().html = Ext.String.format('<b><i>{0}</i></b>: {1}<br />', me.main_tag.get('key'), me.main_tag.get('value'));
        } else {
            // special case: no main tag -> put first of tags instead
            if (me.tags.length > 0) {
                var main_tag = me.tags.pop();
                this._getMainTagPanel().html = Ext.String.format('<b><i>{0}</i></b>: {1}<br />', main_tag.get('key'), main_tag.get('value'))
            }
        }

        /*
        // add button to show or hide 'normal' tags panel
        if (this._getMainTagPanel().html != '' && me.tags.length > 0) {
            this.addDocked({
                dock: 'right',
                xtype: 'toolbar',
                items: [{
                    name: 'toggleDetails',
                    scale: 'small',
                    text: 'details',
                    enableToggle: true,
                    pressed: true,
                    toggleHandler: function(button, state) {
                        // show or hide 'normal' tags panel
                        me._getTagsPanel().setVisible(state);
                    }
                }]
            });
        }
        */
		
        // if user is logged in (Lmkp.toolbar != false), show edit button
        // this is done in controller/Filter.js because it involves data not directly available to this panel.
		
        // all other tags
        if (me.tags.length > 0) {
            var tagspanelHtml = '';
            for (var i=0; i<me.tags.length; i++) {
                tagspanelHtml += Ext.String.format('<b>{0}</b>: {1}<br />', me.tags[i].get('key'), me.tags[i].get('value'));
            }
            this._getTagsPanel().html = tagspanelHtml;
        }
    },
	
    /**
     * Toggle (toggled = true) or unToggle (toggled = false) the button to show or hide 'normal' tags panel
     */
    toggleDetailButton: function(toggled) {
        if (this.down('button[name=toggleDetails]')) {
            this.down('button[name=toggleDetails]').toggle(toggled);
        }
    },
	
    /**
     * Helper method: returns the panel for the main tag.
     */
    _getMainTagPanel: function() {
        if (this.down('panel[name=maintagpanel]')) {
            return this.down('panel[name=maintagpanel]')
        }
    },
	
    /**
     * Helper method: returns the panel for the 'normal' tags.
     */
    _getTagsPanel: function() {
        if (this.down('panel[name=tagspanel]')) {
            return this.down('panel[name=tagspanel]')
        }
    }
});
