Ext.define('Lmkp.utils.StringFunctions', {

    /**
     * Returns a link with the user name or a predefined empty string for null values
     */
    _formatUsername: function(username, userid) {
        if (username == null) {
            return Lmkp.ts.msg('gui_anonymous');
        } else {
            if (userid == null) {
                    return username; // although this hopefully should never happen
            } else {
                    return '<a href="#" onclick="Ext.create(\'Lmkp.view.users.UserWindow\', { username: \'' + username + '\' }).show();">' + username + '</a>';
            }
        }
    },

    /**
     * Returns a nicely formated representation of the timestamp
     */
    _formatTimestamp: function(timestamp, mode) {
        if (timestamp) {
            if (mode == 1) {
                return Ext.Date.format(
                    Ext.Date.parse(timestamp, "Y-m-d H:i:s.u"),
                    "Y/m/d"
                );
            } else {
                return Ext.Date.format(
                    Ext.Date.parse(timestamp, "Y-m-d H:i:s.u"),
                    "Y/m/d H:i"
                );
            }
        }
        return Lmkp.ts.msg('gui_unknown');
    },

    /**
     * Returns a shortened version of the identifier
     */
    _shortenIdentifier: function(identifier) {
        if (identifier) {
            return identifier.substr(0, 6);
        }
        return Lmkp.ts.msg('gui_unknown');
    }
});