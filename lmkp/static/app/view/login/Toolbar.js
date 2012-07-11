Ext.define('Lmkp.view.login.Toolbar' ,{
    extend: 'Ext.toolbar.Toolbar',
    alias : ['widget.lo_logintoolbar'],

    items: [
    Lmkp.login_form,
    '->',{
        xtype: 'combobox',
        fieldLabel: Lmkp.ts.msg("profile-label"),
        labelAlign: 'right',
        id: 'profile_combobox',
        itemId: 'profile_combobox',
        queryMode: 'local',
        store: 'Profiles',
        displayField: 'name',
        valueField: 'profile',
        forceSelection: true
    },{
        xtype: 'combobox',
        fieldLabel: Lmkp.ts.msg("language-label"),
        labelAlign: 'right',
        id: 'language_combobox',
        queryMode: 'local',
        store: 'Languages',
        displayField: 'english_name',
        valueField: 'locale',
        forceSelection: true
    }]
});