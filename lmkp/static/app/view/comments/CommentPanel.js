Ext.define('Lmkp.view.comments.CommentPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.lo_commentpanel',
	
    collapsible: true,
    collapsed: true,
	
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        margin: '3'
    },
	
    // Temporary title
    title: Lmkp.ts.msg('loading'),
	
    bodyStyle: {
        padding: '3px'
    },

    // StringFunctions
    stringFunctions: Ext.create('Lmkp.utils.StringFunctions'),
	
    initComponent: function() {
		
        this.callParent(arguments);
        
        // Show content
        this.loadContent();
		
    },
	
    /**
     * Loads ands adds all the content.
     */
    loadContent: function() {

        var me = this;

        // Remove any existing items (if reloaded)
        if (this.items) {
            this.removeAll();
        }
		
        if (this.identifier && this.comment_object) {
			
            Ext.Ajax.request({
                url: '/comments/' + me.comment_object + '/' + me.identifier,
                method: 'GET',
                success: function(response) {
                    var json = Ext.JSON.decode(response.responseText);
					
                    // Set title
                    me.setTitle(Lmkp.ts.msg('comments') + ' (' + json.total + ')');
                    // If no comments, add empty message
                    if (json.total == 0) {
                        me.add({
                            border: 0,
                            margin: '0 0 5 0',
                            bodyPadding: 5,
                            html: Lmkp.ts.msg('comments-empty')
                        });
						
                    } else {
                        // display comments
                        for (var i in json.comments) {
                            var cc = json.comments[i];
                            // add button do delete if permissions available
                            var docked = null;
                            if (json.can_delete) {
                                docked = {
                                    dock: 'top',
                                    xtype: 'toolbar',
                                    items: ['->', {
                                        text: 'delete',
                                        comment_id: cc.id, // store id of comment
                                        handler: function() {
                                            // show confirmation dialogue
                                            Ext.Msg.confirm(Lmkp.ts.msg('confirm-title'), Lmkp.ts.msg('confirm-delete-comment'), function(btn) {
                                                if (btn == 'yes') {
                                                    Ext.Ajax.request({
                                                        url: '/comments/delete',
                                                        method: 'POST',
                                                        params: {
                                                            'id': this.comment_id
                                                        },
                                                        success: function(response, options) {
                                                            var del_json = Ext.JSON.decode(response.responseText);
                                                            // give feedback
                                                            Ext.Msg.alert(Lmkp.ts.msg('success'), del_json.message);
                                                            // reload comments
                                                            me.loadContent(me);
                                                            // re-layout container
                                                            me._redoLayout();
                                                        },
                                                        failure: function(response, options) {
                                                            var del_json = Ext.JSON.decode(response.responseText);
                                                            // give feedback
                                                            Ext.Msg.alert(Lmkp.ts.msg('failure'), del_json.message);
                                                        }
                                                    });
                                                }
                                            }, this);
                                        }
                                    }]
                                };
                            }
                            me.add({
                                margin: '0 0 5 0',
                                bodyPadding: 5,
                                html: '<span class="grey">'
                                    + Lmkp.ts.msg('comments-by') + ' '
                                    + me.stringFunctions._formatUsername(cc.username, cc.userid)
                                    + ' (' + me.stringFunctions._formatTimestamp(cc.timestamp)
                                    + '):</span><br/><p>' + cc.comment + '</p>',
                                dockedItems: [docked]
                            });
                        }
                    }
					
                    // create the ReCaptcha
                    var recaptcha = Ext.create('Lmkp.view.comments.ReCaptcha', {
                        name: 'recaptcha',
                        recaptchaId: 'recaptcha',
                        publickey: '6LfqmNESAAAAAM1aYTR5LNizhBprFGF0TgyJ43Dw',
                        theme: 'white',
                        lang: Lmkp.ts.msg('locale')
                    });

                    // form to add new comment
                    var form = Ext.create('Ext.form.Panel', {
                        title: Lmkp.ts.msg('comments-leave'),
                        url: '/comments/add',
                        margin: '0 0 5 0',
                        bodyPadding: 5,
                        collapsible: true,
                        collapsed: true,
                        layout: 'anchor',
                        defaults: {
                            anchor: '100%'
                        },
                        items: [{
                            // comment TextArea
                            xtype: 'textareafield',
                            fieldLabel: Lmkp.ts.msg('comment'),
                            name: 'comment',
                            allowBlank: false
                        }, {
                            // captcha (with empty panel for spacing)
                            xtype: 'panel',
                            border: 0,
                            anchor: '100%',
                            layout: {
                                type: 'hbox',
                                flex: 'stretch'
                            },
                            items: [{
                                xtype: 'panel',
                                flex: 1,
                                border: 0
                            },	recaptcha]
                        }, {
                            // object (hidden)
                            xtype: 'hiddenfield',
                            name: 'object',
                            value: 'activity'
                        }, {
                            // identifier (hidden)
                            xtype: 'hiddenfield',
                            name: 'identifier',
                            value: me.identifier
                        }],
                        buttons: [{
                            text: Lmkp.ts.msg('submit'),
                            handler: function() {
                                var form = this.up('form').getForm();
                                if (form.isValid()) {
                                    form.submit({
                                        params: {
                                            recaptcha_challenge_field: recaptcha.getChallenge(),
                                            recaptcha_response_field: recaptcha.getResponse()
                                        },
                                        success: function(form, action) {
                                            // give feedback
                                            Ext.Msg.alert(Lmkp.ts.msg('success'), action.result.message);
                                            // reload comments
                                            me.loadContent(me);
                                            // re-layout container
                                            me._redoLayout();
                                        },
                                        failure: function(form, action) {
                                            // give feedback
                                            Ext.Msg.alert(Lmkp.ts.msg('failure'), action.result.message);
											
                                            // if captcha was wrong, reload it.
                                            if (action.result.captcha_reload) {
                                                Recaptcha.reload();
                                            }
                                        }
                                    });
                                }
                            }
                        }]
                    });
					
                    form.on('expand', function(panel, eOpts) {
                        // re-layout container
                        me._redoLayout();
                    });
					
                    me.add(form);
                },
                failure: function(response, options) {
                    var json = Ext.JSON.decode(response.responseText);
                    // set title
                    me.setTitle(Lmkp.ts.msg('comments'));
                    // show error message
                    me.add({
                        border: 0,
                        html: json.message
                    });
                }
            });
        }
    },
	
    /**
     * Does the layout after items have been removed.
     * (see controller/Filter.js)
     */
    _redoLayout: function() {
        this.forceComponentLayout();
    }
});