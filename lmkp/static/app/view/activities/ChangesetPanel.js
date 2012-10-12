Ext.define('Lmkp.view.activities.ChangesetPanel', {
    extend: 'Ext.form.Panel',
    alias: ['widget.lo_changesetpanel'],

    // General settings
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        margin: 0
    },
    border: 1,
    bodyPadding: 5,
    defaultType: 'displayfield',

    // StringFunctions
    stringFunctions: Ext.create('Lmkp.utils.StringFunctions'),

    initComponent: function() {

        this.items = [
            this.additionalPanelTop,
            {
                fieldLabel: Lmkp.ts.msg('gui_timestamp'),
                value: this._valueOrUnknown(
                    this.stringFunctions._formatTimestamp(this.timestamp)
                )
            }, {
                fieldLabel: Lmkp.ts.msg('gui_version'),
                value: this._valueOrUnknown(this.version)
            }, {
                fieldLabel: Lmkp.ts.msg('gui_previous-version'),
                value: this._valueOrUnknown(this.previous_version)
            }, {
                fieldLabel: Lmkp.ts.msg('gui_user'),
                value: this._valueOrUnknown(
                    this.stringFunctions._formatUsername(
                        this.username, this.userid)
                )
            },
            this.additionalPanelBottom
        ];

        this.callParent(arguments);
    },

    /**
     * Helper function: Returns 'unknown' or value if provided
     */
    _valueOrUnknown: function(v) {
        if (v) {
            return v;
        } else {
            return Lmkp.ts.msg('gui_unknown');
        }
    }

});