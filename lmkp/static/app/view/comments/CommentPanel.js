Ext.define('Lmkp.view.comments.CommentPanel', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.commentpanel',
	
	collapsible: true,
	collapsed: true,
	
	layout: 'anchor',
	defaults: {
		anchor: '100%'
	},
	
	// temporary title
	title: 'Loading ...',
	
	bodyStyle: {
		padding: '5px 5px 0 5px'
	},
	
	initComponent: function() {
		var me = this;
		
		// show content
		this.loadContent(me);
		
		this.callParent(arguments);
	},
	
	loadContent: function(me) {
		
		// remove any existing items (if reloaded)
		if (me.items) {
	    	me.removeAll();
		}
		
		if (me.activity_id) {
			Ext.Ajax.request({
				url: '/comments/activity/' + me.activity_id,
				method: 'GET',
				success: function(response, options) {
					var json = Ext.JSON.decode(response.responseText);
					
					// set title
					me.setTitle('Comments (' + json.total + ')');
					
					// if no comments, add empty message
					if (json.total == 0) {
						me.add({
							border: 0,
							margin: '0 0 5 0',
							bodyPadding: 5,
							html: 'No comments yet.'
						});
						
					} else {
						// prepare template
						var tpl = new Ext.XTemplate(
							'<p>{comment}</p>'
						);
						
						// display comments
						for (var i in json.comments) {
							var cc = json.comments[i];
							me.add({
								margin: '0 0 5 0',
								bodyPadding: 5,
								html: '<span class="grey">Comment by ' + me._formatUsername(cc.username, cc.userid) + ' (' + me._formatTimestamp(cc.timestamp) + '):</span><br/><p>' + cc.comment + '</p>'
							});
						}
					}
					
					// create the ReCaptcha
					var recaptcha = Ext.create('Lmkp.view.comments.ReCaptcha', {
						name: 'recaptcha',
						recaptchaId: 'recaptcha',
						publickey: '6LfqmNESAAAAAM1aYTR5LNizhBprFGF0TgyJ43Dw',
						theme: 'clean',
						lang: 'en'
					});
					
					// form to add new comment
					var form = Ext.create('Ext.form.Panel', {
						title: 'Leave a comment',
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
							fieldLabel: 'Comment',
							name: 'comment',
							allowBlank: false
						},
							// captcha
							recaptcha,
						{
							// object (hidden)
							xtype: 'hiddenfield',
							name: 'object',
							value: 'activity'
						}, {
							// identifier (hidden)
							xtype: 'hiddenfield',
							name: 'identifier',
							value: me.activity_id
						}],
						buttons: [{
							text: 'Submit',
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
											Ext.Msg.alert('Success', action.result.message);
											// reload comments
											me.loadContent(me);
										},
										failure: function(form, action) {
											// give feedback
											Ext.Msg.alert('Failure', action.result.message);
											
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
						// re-layout container (see controller.Filter.js)
						me.ownerCt.layout.layout();
						me.forceComponentLayout();
					});
					
					me.add(form);
				},
				failure: function(response, options) {
					var json = Ext.JSON.decode(response.responseText);
					// set title
					me.setTitle('Comments');
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
	 * Returns a link with the user name or a predefined empty string for null values
	 */
	_formatUsername: function(username, userid) {
		if (username == null) {
			return 'Anonymous';
		} else {
			if (userid == null) {
				return username;
			} else {
				return '<a href="#" onclick="javascript:console.log(\'userid: ' + userid + '\');">' + username + '</a>';
			}
		}
	},
	
	/**
	 * Returns a nicely formated representation of the timestamp
	 */
	_formatTimestamp: function(timestamp) {
		return Ext.Date.format(Ext.Date.parse(timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
	}
});