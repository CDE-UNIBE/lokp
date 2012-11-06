Ext.define('Lmkp.view.stakeholders.NewStakeholderSelection', {
    extend: 'Ext.panel.Panel',

    alias: ['widget.lo_newstakeholderselection'],

    title: Lmkp.ts.msg('stakeholders_add-stakeholders'),

    layout: 'fit',
    defaults: {
        border: 0
    },

    initComponent: function() {

        var form = Ext.create('Ext.form.Panel', {
            autoScroll: true,
            bodyPadding: 5,
            border: 0,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            tbar: [
                {
                    itemId: 'addNewStakeholderButton',
                    scale: 'medium',
                    text: Lmkp.ts.msg('stakeholders_create-new-stakeholder')
                }
            ]
        });

        this.items = form;

        this.callParent(arguments);

    },

	/**
	 * 
 * @param {Object} involvements
	 */
    showForm: function(involvements) {
    	var form = this.down('form');
    	
    	var fieldset = Ext.create('Ext.form.FieldSet', {
    		title: Lmkp.ts.msg('stakeholders_associated-stakeholders'),
            itemId: 'selectStakeholderFieldSet',
            involvements: [] // keep track of all involvements
    	});
    	
    	// If there already are stakeholders, add them to fieldset
    	if (involvements && involvements.length > 0) {
    		for (var i in involvements) {
    			// Make sure the involvement contains a Stakeholder
    			if (involvements[i].stakeholder.modelName 
    				== 'Lmkp.model.Stakeholder') {
    				fieldset.add({
    					involvement: involvements[i],
    					xtype: 'lo_stakeholderfieldcontainer'
    				});
    				// Fieldset is also keeping track of involvements at start
    				fieldset.involvements.push(involvements[i]);
    			}
    		}
    	} else {
    		// If no stakeholders yet, show initial panel
    		this._showInitialText(fieldset);
    	}
    	
        form.add(fieldset,
            {
                xtype: 'lo_stakeholderselection'
            }
        );
    },
    
    _showInitialText: function(fieldset) {
        if (!fieldset) {
            // If not fieldset was provided, try to find it in panel
            fieldset = this.down('fieldset[itemId=selectStakeholderFieldSet]');
        }

        if (fieldset) {
            fieldset.add({
                xtype: 'container',
                itemId: 'initialText',
                html: Lmkp.ts.msg('stakeholders_no-associated-stakeholders-yet')
            });
        }
    }
});