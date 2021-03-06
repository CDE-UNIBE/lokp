<%
    import colander
    empty = True
    thisUid = request.matchdict['uid'] if 'uid' in request.matchdict else ''
%>
% for child in field:
    % if child.cstruct != colander.null and child.name not in ['change', 'reviewable']:
        <%
            empty = False
        %>
        % if child.name == 'role_name':
            <div class="span12">
                <h5 class="compareinvestortitle text-accent-color">
                    ${child.cstruct}
                </h5>
            </div>
        % elif child.name != 'role_id':
            ${child.render_template(field.widget.readonly_item_template)}
        % endif
    % endif
% endfor
% if empty is False and 'reviewable' in cstruct and cstruct['reviewable'] == '-2':
    <div class="span5"></div>
    <div class="span2 inactive"></div>
    <div class="span4">
        <a href="${request.route_url('stakeholders_read_one', output='review', uid=cstruct['id'], _query=(('camefrom', thisUid),))}">
            <i class="icon-check"></i>&nbsp;&nbsp;${_('Review')}
        </a>
    </div>
% endif