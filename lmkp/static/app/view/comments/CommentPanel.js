Ext.define('Lmkp.view.comments.CommentPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.lo_commentpanel',

    /**
     * CONFIGURATION
     */
    // Use captcha or not? Disable for example if no internet connection is
    // available. Also disable on server side (function comment_add in
    // views/comments.py)
    USE_CAPTCHA: false,
	
    bodyPadding: 5,

    collapsible: true,
    collapsed: true,

    config: {
        commentsObject: null
    },
	
    defaults: {
        anchor: '100%',
        margin: '3'
    },

    header: true,

    layout: 'anchor',

    // Temporary title
    title: Lmkp.ts.msg('gui_loading'),
	
    // StringFunctions
    stringFunctions: Ext.create('Lmkp.utils.StringFunctions'),
	
    initComponent: function() {
		
        this.callParent(arguments);

        // Show content
        //this.identifier ? this.loadContent();
        this.commentsObject ? this._renderComments(this.commentsObject) : this._loadContent();

    },
	
    /**
     * Loads ands adds all the content.
     */
    _loadContent: function() {

        console.log("if you ever read this, don't delete this function! (_loadContent)")

        var me = this;

        // Remove any existing items (if reloaded)
        if (this.items) {
            this.removeAll();
        }
		
        if (this.identifier && this.commentType) {

            Ext.Ajax.request({
                url: '/comments/' + me.commentType + '/' + me.identifier,
                method: 'GET',
                failure: function(response, options) {
                    var json = Ext.JSON.decode(response.responseText);
                    // set title
                    me.setTitle(Lmkp.ts.msg('comments_title'));
                    // show error message
                    me.add({
                        border: 0,
                        html: json.message
                    });
                },
                success: function(response) {
                    me.setCommentsObject(Ext.JSON.decode(response.responseText));
                    me._renderComments(me.getCommentsObject());

                    // Inform the enclosing detail window that there's new comments
                    me.up('lo_itemdetailwindow').setItemComment(me.getCommentsObject());
                }
            });
        }
    },

    _renderComments: function(commentObject) {
        //var json = Ext.JSON.decode(response.responseText);
        var json = commentObject;

        var me = this;

        me.removeAll();
					
        // Set title
        me.setTitle(Lmkp.ts.msg('comments_title') + ' (' + json.total + ')');
        // If no comments, add empty message
        if (json.total == 0) {
            me.add({
                border: 0,
                margin: '0 0 5 0',
                bodyPadding: 5,
                html: Lmkp.ts.msg('comments_empty')
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
                                var win = Ext.create('Lmkp.utils.MessageBox');
                                win.confirm(
                                    Lmkp.ts.msg('gui_confirm'),
                                    Lmkp.ts.msg('comments_confirm-delete-comment'),
                                    function(btn) {
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
                                                    Ext.Msg.alert(Lmkp.ts.msg('feedback_success'), del_json.message);
                                                    // reload comments
                                                    me._loadContent(me);
                                                    // re-layout container
                                                    me._redoLayout();
                                                },
                                                failure: function(response, options) {
                                                    var del_json = Ext.JSON.decode(response.responseText);
                                                    // give feedback
                                                    Ext.Msg.alert(Lmkp.ts.msg('feedback_failure'), del_json.message);
                                                }
                                            });
                                        }
                                    }, this
                                );
                            }
                        }]
                    };
                }
                me.add({
                    margin: '0 0 5 0',
                    bodyPadding: 5,
                    html: '<span class="grey">'
                    + Lmkp.ts.msg('comments_comment-by') + ' '
                    + me.stringFunctions._formatUsername(cc.username, cc.userid)
                    + ' (' + me.stringFunctions._formatTimestamp(cc.timestamp)
                    + '):</span><br/><p>' + cc.comment + '</p>',
                    dockedItems: [docked]
                });
            }
        }

        // create the ReCaptcha
        var recaptcha_panel = null;
        if (this.USE_CAPTCHA) {
            recaptcha_panel = Ext.create('Lmkp.view.comments.ReCaptcha', {
                name: 'recaptcha',
                recaptchaId: 'recaptcha',
                publickey: '6LfqmNESAAAAAM1aYTR5LNizhBprFGF0TgyJ43Dw',
                theme: 'white',
                lang: Lmkp.ts.msg('locale')
            });
        }

        // form to add new comment
        var form = Ext.create('Ext.form.Panel', {
            header: true,
            title: Lmkp.ts.msg('comments_leave-comment'),
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
                fieldLabel: Lmkp.ts.msg('comments_singular'),
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
                },
                recaptcha_panel
                ]
            }, {
                // object (hidden)
                xtype: 'hiddenfield',
                name: 'object',
                value: me.commentType
            }, {
                // identifier (hidden)
                xtype: 'hiddenfield',
                name: 'identifier',
                value: me.identifier
            }],
            buttons: [{
                handler: function() {
                    var form = this.up('form').getForm();
                    if (form.isValid()) {

                        var params = null;
                        if (me.USE_CAPTCHA) {
                            params = {
                                recaptcha_challenge_field: recaptcha_panel.getChallenge(),
                                recaptcha_response_field: recaptcha_panel.getResponse()
                            }
                        }
                        
                        form.submit({
                            params: params,
                            success: function(form, action) {
                                // give feedback
                                Ext.Msg.alert(Lmkp.ts.msg('feedback_success'), action.result.message);
                                // reload comments
                                me._loadContent(me);
                                // re-layout container
                                me._redoLayout();
                            },
                            failure: function(form, action) {
                                // give feedback
                                Ext.Msg.alert(Lmkp.ts.msg('feedback_failure'), action.result.message);
											
                                // if captcha was wrong, reload it.
                                if (action.result.captcha_reload) {
                                    Recaptcha.reload();
                                }
                            }
                        });
                    }
                },
                text: Lmkp.ts.msg('button_submit')
            }]
        });
					
        form.on('expand', function(panel, eOpts) {
            // re-layout container
            me._redoLayout();
        });

        me.add(form);
    },
	
    /**
     * Does the layout after items have been removed.
     * (see controller/Filter.js)
     */
    _redoLayout: function() {
        this.forceComponentLayout();
    }
});
