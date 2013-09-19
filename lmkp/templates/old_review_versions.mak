<%inherit file="lmkp:templates/ext_base.mak" />

<%def name="head_tags()">
<title>${_("Land Observatory")} - ${_("Review")}</title>
<style type="text/css">
    table#compare-table{
        width: 98%;
    }
    .remove {
        background-color: lightcoral !important;
    }
    .add {
        background-color: lightgreen !important;
    }
    .button-link {
        background-image: url('/static/img/link.png') !important;
    }
    .button-refresh {
        background-image: url('/static/img/view-refresh.png') !important;
    }
</style>
<script type="text/javascript">
    Ext.ns('Lmkp');
    Lmkp.version = "${metadata['version']}";
</script>
<script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
<script type="text/javascript" src="${request.route_url('moderator_toolbar_config')}"></script>
<script type="text/javascript" src="${request.static_url('lmkp:static/app/reviews.js')}"></script>
</%def>

<div id="loading-mask" style="width: 100%; height: 100%;">
    <div style="position: absolute; top: 50%; right: 50%">
        <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="${_('Loading ...')} ..."/>
    </div>
</div>
<!-- AddThis Button BEGIN -->
<div id="social-plugin">
    <div class="addthis_toolbox addthis_default_style ">
        <a class="addthis_button_facebook_like" fb:like:layout="button_count"></a>
        <a class="addthis_button_tweet"></a>
        <a class="addthis_button_pinterest_pinit"></a>
        <a class="addthis_counter addthis_pill_style"></a>
    </div>
    <script type="text/javascript" src="http://s7.addthis.com/js/300/addthis_widget.js#pubid=xa-50ab9f00139c7215"></script>
    <!-- AddThis Button END -->
</div>