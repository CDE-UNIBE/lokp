Ext.define('Lmkp.view.moderator.Outer' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_moderatorouterpanel'],

    requires: [
    'Lmkp.view.moderator.Main'
    ],

    border: false,
    layout: 'border',

    items: [{
        contentEl: 'header-div',
        height: 80,
        region: 'north',
        xtype: 'panel'
    },{
        region: 'center',
        xtype: 'main'
    }],

    tbar: [Lmkp.login_form
    ,'->', {
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
    }, {
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