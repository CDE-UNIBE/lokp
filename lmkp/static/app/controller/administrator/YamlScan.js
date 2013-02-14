Ext.define('Lmkp.controller.administrator.YamlScan', {
    extend: 'Ext.app.Controller',

    views: [
    'administrator.CodeTab',
    'administrator.Main',
    'administrator.UserManagement',
    'administrator.YamlScan'
    ],
	
    stores: [
    'ActivityYamlScan',
    'StakeholderYamlScan',
    'Languages',
    'Profiles'
    ],
	
    refs: [
        {
            ref: 'profileCombobox',
            selector: 'lo_administratoryamlscanpanel combobox[itemId=yamlScanProfileCombobox]'
        }
    ],
	
    init: function() {
        // Make use of some functions already defined in the translation controller
        var translationController = this.getController('translation.KeyValues');
        this.control({
            'lo_administratoryamlscanpanel toolbar button[itemId=yaml-scan-button]': {
                click: this.doKeyvalueRefresh
            },
            'lo_administratoryamlscanpanel toolbar button[itemId=yaml-add-button]': {
                click: this.onAddButtonClick
            },
            'lo_administratoryamlscanpanel templatecolumn[name=mandatory]': {
                afterrender: translationController.onMandatoryColumnAfterrender
            },
            'lo_administratoryamlscanpanel templatecolumn[name=local]': {
                afterrender: translationController.onLocalColumnAfterrender
            },
            'lo_administratoryamlscanpanel templatecolumn[name=exists]': {
                afterrender: this.onExistsColumnAfterrender
            },
            'lo_administratoryamlscanpanel combobox[itemId=yamlScanProfileCombobox]': {
                select: this.doKeyvalueRefresh
            }
        });
    },

    /**
     * Do the insert of the keys and values to the database and show the result
     * in a window.
     */
    onAddButtonClick: function(button) {
        
        var profileCb = this.getProfileCombobox();
        var profile = profileCb && profileCb.getValue() ? profileCb.getValue() : 'global';
        var treepanel = button.up('panel');

        // Activity or Stakeholder?
        var url;
        if (treepanel.type == 'activity') {
            url = '/config/add/activities';
        } else if (treepanel.type == 'stakeholder') {
            url = '/config/add/stakeholders';
        }

        var win = Ext.create('Ext.window.Window', {
            title: Lmkp.ts.msg('administration_add-all-to-database'),
            closable: true,
            layout: 'fit',
            height: 300,
            width: 400,
            autoScroll: true,
            loader: {
                url: url,
                params: {
                    '_PROFILE_': profile
                },
                loadMask: true,
                autoLoad: true
            },
            buttons: [{
                text: Lmkp.ts.msg('button_ok'),
                handler: function() {
                    this.up('window').hide();
                }
            }]
        });
        win.on('hide', function(){
            this.doKeyvalueRefresh(button);
        }, this);
        win.show();
    },

    /**
     * Do a refresh of the treepanel. Call may come from the refresh button or
     * profile dropdown or after adding keys to DB.
     * comp: button or combobox
     */
    doKeyvalueRefresh: function(comp) {
        var treepanel = comp.up('panel');
        treepanel.setLoading(true);

        var profileCb = this.getProfileCombobox();
        var profile = profileCb && profileCb.getValue() ? profileCb.getValue() : 'global';

        var store = treepanel.getStore();
        store.load({
            node: store.getRootNode(),
            params: {
                '_PROFILE_': profile
            },
            callback: function() {
                treepanel.setLoading(false);
            }
        });
    },

    /**
     * Nicely render the column showing whether a key/value is in DB or not
     * comp: grid cell
     */
    onExistsColumnAfterrender: function(comp) {
        comp.renderer = function(value) {
            if (value == true) {
                return Lmkp.ts.msg('button_yes');
            } else {
                return '<b>' + Lmkp.ts.msg('button_no') + '</b>';
            }
        }
    }
});
