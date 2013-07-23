% for child in field:
    % if field.name == 'primaryinvestor' and child.name == 'role_id':
        <div class="span12">
            <h5 class="green">
                ${_('Primary Investor')}
            </h5>
        </div>
    % elif field.name == 'secondaryinvestor' and child.name == 'role_id':
        <div class="span12">
            <h5 class="green">
                ${_('Secondary Investor')}
            </h5>
        </div>
    % else:
        ${child.render_template(field.widget.readonly_item_template)}
    % endif
% endfor
<div class="span5"></div>
<div class="span2 inactive"></div>
<div class="span4"><a href="/stakeholders/html/${cstruct['id']}">${_('View Stakeholder')}</a></div>