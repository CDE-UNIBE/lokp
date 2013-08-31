<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">Deal Editor</%def>

<%def name="head_tags()">
    <link rel="stylesheet" href="/static/form.css" type="text/css" />

    <script type="text/javascript" src="${request.static_url('lmkp:static/v2/form.js')}"></script>

    <!-- REQUIREMENTS -->
    <!-- CSS -->
    % for reqt in css_links:
        <link rel="stylesheet" href="/formstatic/${reqt}" type="text/css" />
    % endfor
    % for reqt in js_links:
        <script type="text/javascript" src="/formstatic/${reqt}"></script>
    % endfor

    % if js:
        <script type="text/javascript">${js|n}</script>
    % endif
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