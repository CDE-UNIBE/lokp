/**
 * Superclass for Lmkp.view.activities.ActivityPanel and
 * Lmkp.view.stakeholders.StakeholderPanel
 */
Ext.define('Lmkp.view.items.ItemPanel', {
    extend: 'Ext.panel.Panel',

    _addStatusIndicator: function(){
        var status = this.contentItem.get('status');
        switch(status){
            case "pending":
                this.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing a <b>pending</b> version, which needs to be \n\
                        reviewed before it is publicly visible',
                    margin: '3 3 0 3'
                });
                break;
            case 'inactive':
                this.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing an <b>inactive</b> version, which was previously active.',
                    margin: '3 3 0 3'

                });
                break;
            case 'deleted':
                this.add({
                    bodyCls: 'warning',
                    bodyPadding: 5,
                    html: 'You are seeing a <b>deleted</b> version.',
                    margin: '3 3 0 3'

                });
                break;
            case 'rejected':
                this.add({
                    bodyCls: 'warning',
                    bodyPadding: 5,
                    html: 'You are seeing a <b>rejected</b> version.',
                    margin: '3 3 0 3'

                });
                break;
            case 'edited':
                this.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing an <b>edited</b> version.',
                    margin: '3 3 0 3'

                });
                break;
        }
    }
});