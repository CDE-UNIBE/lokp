Ext.define('Lmkp.view.activities.TagGroupPanel', {
    extend: 'Ext.form.Panel',
    alias: 'widget.lo_taggrouppanel',
	
    layout: 'anchor',
    
    config: {
        editable: true  
    },
    
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

            if (this.taggroup.get('id') != 0) {
                // Tag group is not empty

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

                // Add buttons to edit TagGroup
                if (this.editable) {
                    me.addDocked({
                        dock: 'top',
                        xtype: 'toolbar',
                        items: ['->',
                            {
                            name: 'editTaggroup',
                            text: Lmkp.ts.msg('button_edit'),
                            selected_taggroup: this.taggroup
                            }
                        ]
                    });
                }
                
            } else {
                // Tag group is empty
                me.add({
                    xtype: 'panel',
                    html: Lmkp.ts.msg('gui_no-attributes'),
                    border: 0
                });
            }
        }
    },

    _getTagPanel: function(key, value, is_main_tag) {
                
        // FILES
        // Tags with key == 'Files' need to be rendered separately
        if (Lmkp.ts.msg('activity_db-key-files') == key) {
            var values = Ext.JSON.decode(value);
            value = '';
            for (var v in values) {
                // Show the filename
                value += values[v].name;
                // Show a link to view the file
                var view_url = '/files/view/' + values[v].identifier;
                var view_title = Lmkp.ts.msg('tooltip_view-file');
                value += '&nbsp;<a class="file-view-button" title="' + view_title + '" href="' + view_url + '" target="_blank">&nbsp;</a>'
                // Show a link to download the file
                var download_url = 'files/download/' + values[v].identifier;
                var download_title = Lmkp.ts.msg('tooltip_download-file');
                value += '&nbsp;<a class="file-download-button" title="' + download_title + '" href="' + download_url + '" target="_blank">&nbsp;</a>'
                value += '</br>';
            }
        }

        return {
            name: is_main_tag ? 'main_tag_panel' : 'tag_panel',
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

    _toggleTags: function(toggle) {
        var panels = this.query('displayfield[name=tag_panel]');
        for (var i in panels) {
            panels[i].setVisible(toggle);
        }
    },
	
    /**
     * Toggle (toggle = true) or unToggle (toggled = false) the button to show or hide 'normal' tags panel
     */
    _toggleDetailButton: function(toggle) {
        if (this.down('button[name=toggleDetails]')) {
            this.down('button[name=toggleDetails]').toggle(toggle);
        }
    }
});
