/**
 * Super class for Lmkp.view.activities.Details and
 * Lmkp.view.stakeholders.Details.
 */
Ext.define('Lmkp.view.items.Details',{
    extend: 'Ext.window.Window',
    alias: ['widget.lo_itemdetailwindow'],

    bbar: {
        items: ['->', {
            iconCls: 'cancel-button',
            itemId: 'closeWindowButton',
            scale: 'medium',
            text: Lmkp.ts.msg('button_close'),
            tooltip: Lmkp.ts.msg('tooltip_close-window')
        }],
        xtype: 'toolbar'
    },

    bodyPadding: 5,

    centerPanelType: null,

    config: {
        /**
         * XType of the comment panel that will be inserted.
         */
        commentPanelType: null,
        /**
         * A comment object for this item (activity resp. stakeholder). The object
         * is the result from a /comments/activity/{id} resp.
         * /comments/stakeholder/{id} request.
         * It is set (so far only for Activities) when rendering the window.
         */
        itemComment: null
    },

    defaults: {
        margin: '0 0 5 0',
        anchor: '100%'
    },

    layout: 'border',
    modal: true,

    /**
     * Ext has some serious issues with panels collapsed on start. Instead, this
     * function is called right after showing this window.
     */
    _collapseHistoryPanel: function() {
        if (this.historyPanel) {
            this.historyPanel.collapse();
        }

        return this;
    },


    /**
     * Parameter stakeholder is an instance of Lmkp.model.Stakeholder
     */
    _populateDetails: function(item){

        if (item) {

            // Set the current selection to current
            this.current = item;

            // Remove all existing panels
            this.centerPanel.removeAll();

            // If there are no versions pending, simply show active version
            this.centerPanel.add({
                contentItem: item,
                border: 0,
                bodyPadding: 0,
                editable: true,
                hiddenOriginal: false,
                xtype: this.centerPanelType
            });

            var identifier = item.get('identifier');
            if (!identifier) {
                identifier = item.get('id');
            }
            this._populateComment(identifier, item.modelName);
        }

        return item;

    },

    _populateComment: function(identifier, modelName){

        // First check if there is already an existing comment panel and remove
        // it if yes.
        var cp = this.centerPanel.down('panel[id="comment-panel"]');
        if(cp){
            this.centerPanel.remove(cp);
        }

        Ext.Ajax.request({
            method: 'GET',
            scope: this,
            success: function(response) {
                // Set the comment for this activity to the detail window
                var r = Ext.JSON.decode(response.responseText);

                var site_key = r.site_key;

                var commentPanel = this.centerPanel.add({
                    id: 'comment-panel',
                    html: 'Loading comments ...',
                    listeners: {
                        render: function(comp){

                            // The following parts of code are taken from the
                            // Juvia GitHub repository:
                            // http://juvia-demo.phusion.nl/admin/help/embedding
                            var options = {
                                container   : '#comment-panel',
                                site_key    : site_key,
                                topic_key   : identifier,
                                topic_url   : location.href,
                                topic_title : document.title + " " + identifier,
                                include_base: !window.Juvia,
                                include_css : !window.Juvia
                            };

                            function makeQueryString(options) {
                                var key, params = [];
                                for (key in options) {
                                    params.push(
                                        encodeURIComponent(key) +
                                        '=' +
                                        encodeURIComponent(options[key]));
                                }
                                return params.join('&');
                            }

                            function makeApiUrl(options) {
                                // Makes sure that each call generates a unique URL, otherwise
                                // the browser may not actually perform the request.
                                if (!('_juviaRequestCounter' in window)) {
                                    window._juviaRequestCounter = 0;
                                }

                                var result =
                                Lmkp.comments_url + 'api/show_topic.js' +
                                '?_c=' + window._juviaRequestCounter +
                                '&' + makeQueryString(options);
                                window._juviaRequestCounter++;
                                return result;
                            }

                            var s       = document.createElement('script');
                            s.async     = true;
                            s.type      = 'text/javascript';
                            s.className = 'juvia';
                            s.src       = makeApiUrl(options);
                            (document.getElementsByTagName('head')[0] ||
                                document.getElementsByTagName('body')[0]).appendChild(s);
                        }
                    },
                    margin: 3,
                    xtype: 'container'
                });
            },
            url: '/comments/sitekey/' + identifier
        });
        
    }

});