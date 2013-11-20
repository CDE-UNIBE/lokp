<%
    import colander
    empty = True
%>
% for child in field:
    <%doc>
    % if child.name == 'role_name':
        <div class="span12">
            <h5 class="green">
                ${child.cstruct}
            </h5>
        </div>
    % elif child.name != 'role_id':
        ${child.render_template(field.widget.readonly_item_template)}
    % endif
    </%doc>
    % if child.cstruct != colander.null:
        <%
            empty = False
        %>
        ${child.render_template(field.widget.readonly_item_template)}
    % endif
% endfor
% if empty is False:
    <div class="span5"></div>
    <div class="span2 inactive"></div>
    <div class="span4"><a href="/stakeholders/html/${cstruct['id']}">${_('View Stakeholder')}</a></div>
% else:
    -
% endif