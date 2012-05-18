Ext.define('Lmkp.view.comments.CommentPanel', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.commentpanel',
	
	collapsible: true,
	collapsed: true,
	
	bodyStyle: {
		padding: '5px 5px 0 5px'
	},
	
	initComponent: function() {
		var me = this;
		
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
								html: '<span class="grey">Comment by ' + me._formatUsername(cc.username, cc.userid) + ' at ' + me._formatTimestamp(cc.timestamp) + ':</span><br/><p>' + cc.comment + '</p>'
							});
						}
					}
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
		
		this.callParent(arguments);
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