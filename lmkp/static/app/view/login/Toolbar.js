Ext.define('Lmkp.view.login.Toolbar' ,{
    extend: 'Ext.toolbar.Toolbar',
    alias : ['widget.lo_logintoolbar'],

    defaults: {
        labelWidth: 60,
        xtype: 'combobox'
    },

    items: [{
        fieldLabel: Lmkp.ts.msg("gui_profile"),
        id: 'profile_combobox',
        itemId: 'profile_combobox',
        queryMode: 'local',
        store: 'Profiles',
        displayField: 'name',
        valueField: 'profile',
        forceSelection: true,
        editable: false
    },{
        fieldLabel: Lmkp.ts.msg("gui_language"),
        id: 'language_combobox',
        queryMode: 'local',
        store: 'Languages',
        displayField: 'local_name',
        valueField: 'locale',
        forceSelection: true,
        editable: false
    }, '->', Lmkp.login_form]
});