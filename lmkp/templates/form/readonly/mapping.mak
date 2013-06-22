% for child in field:
    % if field.name == 'primaryinvestor' and child.name == 'role_id':
        <div class="span5">
            <h5 class="green">
                Primary Investor
            </h5>
        </div>
        <div class="span2 inactive"></div>
        <div class="span4"></div>
    % elif field.name == 'secondaryinvestor' and child.name == 'role_id':
        <div class="span5">
            <h5 class="green">
                Secondary Investor
            </h5>
        </div>
        <div class="span2 inactive"></div>
        <div class="span4"></div>
    % else:
        ${child.render_template(field.widget.readonly_item_template)}
    % endif
% endfor
