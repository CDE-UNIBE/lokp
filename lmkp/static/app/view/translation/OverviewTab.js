Ext.define('Lmkp.view.translation.OverviewTab', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.lo_translationoverviewtab',

    bodyPadding: 10,

    title: Lmkp.ts.msg('gui_overview'),

    // TODO
    html: '\
        <b>Welcome, translator!</b>\n\
        <p>&nbsp;</p>\n\
        <p>Here you will soon find some more information about the translation process.</p>\n\
        <p>&nbsp;</p>\n\
        <p>For translation of the GUI text, please visit <a href="http://www.poeditor.com">POEditor</a></p>'

});