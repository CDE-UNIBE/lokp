<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">Stakeholder Editor</%def>

<%def name="head_tags()">

    <link rel="stylesheet" href="/static/form.css" type="text/css" />

    <script type="text/javascript" src="${request.static_url('lmkp:static/v2/form.js')}"></script>

    <%
        if 'scripts/jquery-ui-1.8.11.custom.min.js' not in js_links:
            js_links.append('scripts/jquery-ui-1.8.11.custom.min.js')
    %>

    % for reqt in js_links:
        <script type="text/javascript" src="/formstatic/${reqt}"></script>
    % endfor
</%def>

<div class="container deal-edit-content">
    <div class="content no-border">
        ${form | n}
    </div>
</div>

<%def name="bottom_tags()">
    <script type="text/javascript">
       deform.load();
    </script>
</%def>
