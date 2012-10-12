Ext.define('Lmkp.view.stakeholders.NewStakeholder', {
    extend: 'Lmkp.view.items.NewItem',

    alias: ['widget.lo_newstakeholderpanel'],

    layout: 'fit',
    defaults: {
        border: 0
    },

    width: 400,

    initComponent: function(){

        //var form = this.down('form');
        // prepare the form
        var form = Ext.create('Ext.form.Panel', {
            itemId: 'newStakeholderForm',
            autoScroll: true,
            border: 0,
            bodyPadding: 5,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            tbar: [
                {
                    iconCls: 'add-info-button',
                    itemId: 'addAdditionalTaggroupButton',
                    scale: 'medium',
                    text: Lmkp.ts.msg('button_add-new-taggroup')
                }
            ],
            buttons: [{
                iconCls: 'cancel-button',
                scale: 'medium',
                text: Lmkp.ts.msg('button_cancel'),
                itemId: 'cancelButton'
            },{
                disabled: true,
                formBind: true,
                iconCls: 'save-button',
                itemId: 'submitButton',
                scale: 'medium',
                scope: this,
                text: Lmkp.ts.msg('button_submit')
            }]
        });

        this.items = form;
        
        this.callParent(arguments);
    },

    /**
     * {item}: Optional possibility to provide an existing item (instance of
     * model.Stakeholder)
     * Actually this function (and the ones below) are very similar as in
     * NewActivity.js, maybe they could be put together somehow (in NewItem.js
     * ?)
     */
    showForm: function(mandatoryStore, completeStore, item) {

        var me = this;
        var form = this.down('form');

        // Delete all existing items
        form.removeAll();

        // A separate store is needed for each taggroup. Instead of
        // loading a new ActivityConfig store (and querying the server)
        // each time, copy all the entries of the complete store and add
        // them manually to each store.
        var records = [];
        completeStore.each(function(r) {
            records.push(r.copy());
        });

        if (item != null && item.modelName == 'Lmkp.model.Stakeholder') {
            // Edit item. Show previous Tag Groups

            // Flag to show if some tags were not displayed because they are not
            // in current profile
            var profile_info = null;

            // Store Stakeholder identifiert and version (needed for diff)
            form.stakeholder_identifier = (item) ? item.get('id') : null;
            form.stakeholder_version = (item) ? item.get('version') : null;
            form.taggroups = [];

            // In a first step, it is necessary to collect only the tags of
            // current profile

            // Go through each taggroup
            var taggroups = item.taggroups();
            taggroups.each(function(taggroup) {

                var store = Ext.create('Lmkp.store.StakeholderConfig');
                store.add(records);

                var tempTags = [];
                var tempMainTag = {};

                // Go through each tag
                var tags = taggroup.tags();
                tags.each(function(tag) {
                    // Only keep track of attributes available in
                    // configuration store
                    if (completeStore.find('fieldLabel', tag.get('key')) != -1) {
                        // Treat main tags and 'normal' tags differently
                        if (taggroup.main_tag().first() &&
                            tag.get('id') == taggroup.main_tag().first().get('id')) {
                            tempMainTag = tag;
                        } else {
                            tempTags.push(tag);
                        }
                    } else {
                        // Show a message that at least one attribute is
                        // not shown because of profile
                        profile_info = true;
                    }
                });

                // Collect items for the form
                var formMainTag = null;
                var formTags = (tempTags.length > 0) ? [] : null;

                // Form: Main Tag
                if (tempMainTag && tempMainTag.isModel) {
                    if (tempMainTag.get('key') && tempMainTag.get('value')
                        && tempMainTag.get('id')) {
                        formMainTag = {
                            xtype: 'lo_newtaggrouppanel',
                            is_maintag: true,
                            removable: true,
                            main_store: store,
                            complete_store: completeStore,
                            initial_key: tempMainTag.get('key'),
                            initial_value: tempMainTag.get('value'),
                            initial_tagid: tempMainTag.get('id')
                        };
                    }
                }

                // Form: normal Tags
                for (var t in tempTags) {
                    formTags.push({
                        xtype: 'lo_newtaggrouppanel',
                        is_maintag: false,
                        removable: true,
                        main_store: store,
                        complete_store: completeStore,
                        initial_key: tempTags[t].get('key'),
                        initial_value: tempTags[t].get('value'),
                        initial_tagid: tempTags[t].get('id')
                    });
                }

                // Prepare fieldset
                var fieldset = me._getFieldset(
                    tempTags.concat(tempMainTag),
                    taggroup.get('id')
                );
                fieldset.add(formMainTag);
                fieldset.add(formTags);

                // Add fieldset to form
                form.add(fieldset);

                // Store visible Tag Group (needed for diff)
                form.taggroups.push({
                    id: taggroup.get('id'),
                    tags: tempTags.concat(tempMainTag)
                });

                // In the end, show information if some attributes were skipped
                // because of profile
                if (profile_info) {
                    form.insert(0, {
                        xtype: 'panel',
                        html: Lmkp.ts.msg('feedback_some-attributes-not-editable-because-of-profile'),
                        bodyCls: 'notice',
                        bodyPadding: 5,
                        margin: '0 0 5 0'
                    });
                }
            });

        } else {
            // No item to edit. Show all new fields.

            // Add a fieldset for each mandatory Key
            mandatoryStore.each(function(record) {
                // All keys should be available for each fieldset -> 'copy' store
                var main_store = Ext.create('Lmkp.store.StakeholderConfig');
                main_store.add(records);

                var fieldset = me._getFieldset();
                fieldset.add(me._getSingleFormItem(
                    main_store,
                    completeStore,
                    record.get('name'),
                    true
                ));
                form.add(fieldset);
            });
        }
    },

    /**
     * Returns the basic fieldset (which is actually a 'form') to display the
     * form items of a Tag Group.
     */
    _getFieldset: function(oldTags, taggroupId) {
        return Ext.create('Ext.form.Panel', {
            oldTags: oldTags,
            taggroupId: taggroupId,
            name: 'taggroupfieldset',
            bodyPadding: 5,
            margin: '0 0 10 0',
            defaults: {
                margin: 0
            },
            // Toolbar to add additional Tags to Tag Group
            tbar: ['->',
                {
                    xtype: 'button',
                    name: 'addAdditionalTagButton',
                    text: Lmkp.ts.msg('button_add-new-tag')
                }
            ]
        });
    },

    /**
     * Returns a single form entry.
     * {is_mandatory}: Boolean. Renders the combobox of the newtaggrouppanel
     * disabled (cannot be changed)
     */
    _getSingleFormItem: function(mainStore, completeStore, initial_key,
        is_mandatory) {
        return {
            xtype: 'lo_newtaggrouppanel', // This should be named tagpanel
            is_maintag: true,
            removable: true,
            main_store: mainStore,
            complete_store: completeStore,
            initial_key: initial_key,
            is_mandatory: is_mandatory
        };
    }

});