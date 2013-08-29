<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">${_('Stakeholder Details')} ${shortuid}</%def>

<%def name="head_tags()">
<style type="text/css" >
    /* Some nasty temporary css hacks */
    p.deal-detail {
        font-weight: normal;
    }
    .row-fluid [class*="span"]:first-child {
        margin-left: 10px;
    }
    .row-fluid [class*="span"] {
        margin-left: 10px;
    }
    .row-fluid [class*="span"]:first-child [class*="span"]:first-child h5 {
        color: #A3A708;
        font-weight: bold;
    }
    .row-fluid [class*="span"] h5 {
        font-weight: normal;
    }
    .juvia-topic > h3 {
        font-size: 14px;
    }
    .juvia-preview > h4 {
        font-size: 14px;
    }
</style>
</%def>

<div class="container">
    <div class="content no-border">
        ${form | n}
    </div>
    %if site_key is not None:
    <div id="comments-div" class="comments content no-border">
        ${_('Loading ...')}
    </div>
    %endif
</div>

<%def name="bottom_tags()">

%if site_key is not None:
<script type="text/javascript" class="juvia">
    (function() {
        var options = {
            container: "#comments-div",
            site_key: "${site_key}",
            topic_key   : "${uid}",
            topic_url   : location.href,
            topic_title : document.title || location.href,
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
                "${comments_url}/api/show_topic.js" +
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
    })();
</script>
%endif

</%def>
