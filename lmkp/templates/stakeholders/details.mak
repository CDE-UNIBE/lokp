<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Stakeholder Details</%def>

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
    </style>
</%def>

<div class="container">
    <div class="content no-border">
        ${form | n}
    </div>
</div>