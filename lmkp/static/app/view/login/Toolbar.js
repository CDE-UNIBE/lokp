/**
 * View for the login toolbar at the top of the application.
 * The profile combobox is hidden if Lmkp.is_embedded is set to true. This
 * combobox can also be hidden manually by using  'hideProfileSelection = true'.
 */

Ext.define('Lmkp.view.login.Toolbar' ,{
    extend: 'Ext.toolbar.Toolbar',
    alias : ['widget.lo_logintoolbar'],

    defaults: {
        labelWidth: 60,
        xtype: 'combobox'
    },

    requires: [
        'Ext.util.*'
    ],

    initComponent: function() {
        var items = [{
            fieldLabel: Lmkp.ts.msg("gui_profile"),
            id: 'profile_combobox',
            itemId: 'profile_combobox',
            queryMode: 'local',
            store: 'Profiles',
            displayField: 'name',
            value: Ext.util.Cookies.get('_PROFILE_') ? Ext.util.Cookies.get('_PROFILE_') : 'global',
            valueField: 'profile',
            forceSelection: true,
            editable: false,
            // Hide this combobox if the application is embedded
            hidden: Lmkp.is_embedded || this.hideProfileSelection
        },{
            fieldLabel: Lmkp.ts.msg("gui_language"),
            id: 'language_combobox',
            queryMode: 'local',
            store: 'Languages',
            displayField: 'local_name',
            value: Lmkp.ts.msg("locale"),
            valueField: 'locale',
            forceSelection: true,
            editable: false
        }, '->', Lmkp.login_form];
        this.items = items;
        this.callParent(arguments);
    }
});