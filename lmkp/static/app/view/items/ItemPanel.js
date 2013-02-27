/**
 * Superclass for Lmkp.view.activities.ActivityPanel and
 * Lmkp.view.stakeholders.StakeholderPanel
 */
Ext.define('Lmkp.view.items.ItemPanel', {
    extend: 'Ext.panel.Panel',

    _addStatusIndicator: function(){
        var status = this.contentItem.get('status_id');
        switch(status){
            case 1:
                this.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html:
                        Lmkp.ts.msg(
                            'gui_currently-seeing-pending-version'
                        ).replace(
                            '{0}',
                            '<b>' + Lmkp.ts.msg('status_pending') + '</b>'
                        ),
                    margin: '3 3 0 3'
                });
                break;
            case 3:
                this.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html:
                        Lmkp.ts.msg(
                            'gui_currently-seeing-inactive-version'
                        ).replace(
                            '{0}',
                            '<b>' + Lmkp.ts.msg('status_inactive') + '</b>'
                        ),
                    margin: '3 3 0 3'

                });
                break;
            case 4:
                this.add({
                    bodyCls: 'warning',
                    bodyPadding: 5,
                    html:
                        Lmkp.ts.msg(
                            'gui_currently-seeing-deleted-version'
                        ).replace(
                            '{0}',
                            '<b>' + Lmkp.ts.msg('status_deleted') + '</b>'
                        ),
                    margin: '3 3 0 3'

                });
                break;
            case 5:
                this.add({
                    bodyCls: 'warning',
                    bodyPadding: 5,
                    html:
                        Lmkp.ts.msg(
                            'gui_currently-seeing-rejected-version'
                        ).replace(
                            '{0}',
                            '<b>' + Lmkp.ts.msg('status_rejected') + '</b>'
                        ),
                    margin: '3 3 0 3'

                });
                break;
            case 6:
                this.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html:
                        Lmkp.ts.msg(
                            'gui_currently-seeing-edited-version'
                        ).replace(
                            '{0}',
                            '<b>' + Lmkp.ts.msg('status_edited') + '</b>'
                        ),
                    margin: '3 3 0 3'

                });
                break;
        }
    }
});