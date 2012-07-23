Ext.define('Lmkp.view.activities.TagGroupPanel', {
    extend: 'Ext.form.Panel',
    alias: 'widget.lo_taggrouppanel',
	
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        margin: 0
    },
    bodyPadding: 5,
    defaultType: 'displayfield',
	
    initComponent: function() {

        var me = this;

        // Start with empty panel
        me.items = [];
        this.callParent(arguments);

        // Add a field for each Tag of current TagGroup
        if (this.taggroup) {

            // First: main tag
            var main_tag = this.taggroup.main_tag().first();
            if (main_tag) {
                me.add(me._getTagPanel(
                    main_tag.get('key'), main_tag.get('value'), true
                ));
            }

            // Second: all other tags (don't repeat main tag)
            var tStore = this.taggroup.tags();
            tStore.each(function(record) {
                if (!main_tag || record.get('id') != main_tag.get('id')) {
                    me.add(me._getTagPanel(
                        record.get('key'), record.get('value')
                    ));
                }
            });

            // Add button to edit TagGroup
            me.addDocked({
                dock: 'top',
                xtype: 'toolbar',
                items: ['->',
                    {
                        name: 'editTaggroup',
                        text: 'edit',
                        selected_taggroup: this.taggroup
                    }
                ]
            });
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

    },

    _getTagPanel: function(key, value, is_main_tag) {
        return {
            xtype: 'displayfield',
            fieldLabel: key,
            value: value,
            style: this._getMainTagStyle(is_main_tag)
        }
    },

    _getMainTagStyle: function(is_main_tag) {
        var style = null;
        if (is_main_tag) {
            style = {
                'font-weight': 'bold'
            };
        }
        return style;
    },
	
    /**
     * Toggle (toggled = true) or unToggle (toggled = false) the button to show or hide 'normal' tags panel
     */
    toggleDetailButton: function(toggled) {
        if (this.down('button[name=toggleDetails]')) {
            this.down('button[name=toggleDetails]').toggle(toggled);
        }
    }
});
