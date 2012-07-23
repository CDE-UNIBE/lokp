Ext.define('Lmkp.view.stakeholders.Filter', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editorstakeholderfilterpanel'],

    id: 'stakeholderFilterForm',
    flex: 0.5,
    border: 0,
    title: Lmkp.ts.msg('filter-stakeholder_title'),
    layout: {
        type: 'anchor'
    },
    defaults: {
        anchor: '100%',
        border: 0
    },
    bodyPadding: 5,
    items: [
        {
            xtype: 'panel',
            html: 'coming soon'
        }
    ]
});