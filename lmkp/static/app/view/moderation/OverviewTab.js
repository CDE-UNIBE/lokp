Ext.define('Lmkp.view.moderation.OverviewTab', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.lo_moderationoverviewtab',

    title: Lmkp.ts.msg('gui_overview'),

    // TODO
    html: '<b>Welcome, moderator!</b><p>&nbsp;</p><p>Here you will soon find some more help about the moderation process and other useful information such as the number of pending items, the number of comments to review (and link to moderation of comments).</p>'

});