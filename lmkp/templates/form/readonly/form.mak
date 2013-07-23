<%
    isStakeholder = 'itemType' in cstruct and cstruct['itemType'] == 'stakeholders'
    statusId = cstruct['statusId'] if 'statusId' in cstruct else '2'

    from pyramid.security import ACLAllowed
    from pyramid.security import has_permission
    isModerator = isinstance(has_permission('moderate', request.context, request), ACLAllowed)
%>

% if statusId != '2':
    <div class="row-fluid">
        <div class="span9">
            <div class="alert alert-block">
                % if statusId == '1':
                    ## Pending
                    <h4>${_('Pending Version')}</h4>
                    <p>${_('You are seeing a pending version which needs to be reviewed before it is publicly visible.')}</p>
                % elif statusId == '3':
                    ## Inactive
                    <h4>${_('Inactive Version')}</h4>
                    <p>${_('You are seeing an inactive version which is not active anymore.')}</p>
                % else:
                    ## All the rest (deleted, rejected, edited).
                    ## TODO: Should there be a separate messages for these statuses?
                    <h4>${_('Not an active Version')}</h4>
                    <p>${_('You are seeing a version which is not active.')}</p>
                % endif
            </div>
        </div>
    </div>
% endif

<div class="row-fluid">
    <div class="span6">
        % if isStakeholder:
            <h3>${_('Stakeholder Details')}</h3>
        % else:
            <h3>${_('Deal Details')}</h3>
        % endif
    </div>
    <div class="span3 text-right">
        % if request.user and 'id' in cstruct:
            % if isStakeholder:
                % if isModerator and statusId == '1':
                    <a href="${request.route_url('stakeholders_moderate_item', uid=cstruct['id'])}" target="_blank">
                        <i class="icon-check">&nbsp;&nbsp;${_('Review this version')}</i>
                    </a><br/>
                % endif
                <a href="${request.route_url('stakeholders_read_one', output='form', uid=cstruct['id'])}">
                    <i class="icon-pencil"></i>&nbsp;&nbsp;${_('Edit this')} ${_('Investor')}
                </a>
            % else:
                % if isModerator and statusId == '1':
                    <a href="${request.route_url('activities_moderate_item', uid=cstruct['id'])}" target="_blank">
                        <i class="icon-check">&nbsp;&nbsp;${_('Review this version')}</i>
                    </a><br/>
                % endif
                <a href="${request.route_url('activities_read_one', output='form', uid=cstruct['id'])}">
                    <i class="icon-pencil"></i>&nbsp;&nbsp;${_('Edit this')} ${_('Deal')}
                </a>
            % endif
        % endif
    </div>
</div>
<div class="row-fluid">
    % if 'id' in cstruct:
        <div class="span9">
            <p class="id">${cstruct['id']}</p>
        </div>
    % endif
</div>

% if not isStakeholder:
    ## Map container
    <div class="row-fluid">
        <div class="span9 map-not-whole-page">
            <div id="googleMapNotFull"></div>
        </div>
    </div>
% endif

% for child in field:
    ${child.render_template(field.widget.readonly_item_template)}
% endfor

% if request.user and 'id' in cstruct:
    <p>&nbsp;</p>
    <div class="row-fluid">
        % if isStakeholder:
            <a href="${request.route_url('stakeholders_read_one', output='form', uid=cstruct['id'])}">
                <i class="icon-pencil"></i>&nbsp;&nbsp;${_('Edit this')} ${_('Investor')}
            </a>
            % if isModerator and statusId == '1':
                &nbsp;|&nbsp;<a href="${request.route_url('stakeholders_moderate_item', uid=cstruct['id'])}" target="_blank">
                    <i class="icon-check">&nbsp;&nbsp;${_('Review this version')}</i>
                </a>
            % endif
        % else:
            <a href="${request.route_url('activities_read_one', output='form', uid=cstruct['id'])}">
                <i class="icon-pencil"></i>&nbsp;&nbsp;${_('Edit this')} ${_('Deal')}
            </a>
            % if isModerator and statusId == '1':
                &nbsp;|&nbsp;<a href="${request.route_url('activities_moderate_item', uid=cstruct['id'])}" target="_blank">
                    <i class="icon-check">&nbsp;&nbsp;${_('Review this version')}</i>
                </a>
            % endif
        % endif
    </div>
% endif
