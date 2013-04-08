Ext.define('Lmkp.view.administrator.OverviewTab', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.lo_administratoroverviewtab',

    bodyPadding: 10,

    title: Lmkp.ts.msg('gui_overview'),

    // TODO
    html: '\
        <b>Welcome, administrator!</b>\n\
        <p>&nbsp;</p>\n\
        <p>Here you will soon find some more information about the administration process.</p>'

});