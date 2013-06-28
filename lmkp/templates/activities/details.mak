<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Deal Details</%def>

<%def name="head_tags()">
    <style type="text/css" >
        .olTileImage {
            max-width: none !important;
        }
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

    </style>
</%def>

<div class="container">
    <div class="content no-border">
        ${form | n}
    </div>
</div>

<%def name="bottom_tags()">

    <%include file="lmkp:templates/map/mapform.mak" args="readonly=True" />

</%def>
