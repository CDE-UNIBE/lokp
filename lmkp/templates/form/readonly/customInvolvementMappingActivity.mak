% for child in field:
    % if child.name == 'role_name':
        <div class="span12">
            <h5 class="green">
                ${_('Involvement as')} ${child.cstruct}
            </h5>
        </div>
    % elif child.name != 'role_id':
        ${child.render_template(field.widget.readonly_item_template)}
    % endif
% endfor
<div class="span5"></div>
<div class="span2 inactive"></div>
<div class="span4"><a href="/activities/html/${cstruct['id']}">${_('View Deal')}</a></div>