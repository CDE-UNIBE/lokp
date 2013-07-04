% for child in field:
    % if field.name == 'primaryinvestors' and child.name == 'role_id':
        <div class="span12">
            <h5 class="green">
                Involvement as Primary Investor
            </h5>
        </div>
    % elif field.name == 'secondaryinvestors' and child.name == 'role_id':
        <div class="span12">
            <h5 class="green">
                Involvement as Secondary Investor
            </h5>
        </div>
    % else:
        ${child.render_template(field.widget.readonly_item_template)}
    % endif
% endfor
<div class="span5"></div>
<div class="span2 inactive"></div>
<div class="span4"><a href="/activities/html/${cstruct['id']}">View Deal</a></div>