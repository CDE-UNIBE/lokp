<%
    isStakeholder = 'itemType' in cstruct and cstruct['itemType'] == 'stakeholders'
    statusId = cstruct['statusId'] if 'statusId' in cstruct else '2'
%>

% if statusId != '2':
    <div class="row-fluid">
        <div class="span9">
            <div class="alert alert-block">
                % if statusId == '1':
                    ## Pending
                    <h4>Pending Version</h4>
                    <p>You are seeing a pending version which needs to be reviewed before it is publicly visible.</p>
                % elif statusId == '3':
                    ## Inactive
                    <h4>Inactive Version</h4>
                    <p>You are seeing an inactive version which is not active anymore.</p>
                % else:
                    ## All the rest (deleted, rejected, edited).
                    ## TODO: Should there be a separate messages for these statuses?
                    <h4>Not an active Version</h4>
                    <p>You are seeing a version which is not active.</p>
                % endif
            </div>
        </div>
    </div>
% endif

<div class="row-fluid">
    <div class="span6">
        % if isStakeholder:
            <h3>Stakeholder Details</h3>
        % else:
            <h3>Deal Details</h3>
        % endif
    </div>
    <div class="span3 text-right">
        % if request.user and 'id' in cstruct:
            % if isStakeholder:
                <a href="${request.route_url('stakeholders_read_one', output='form', uid=cstruct['id'])}">
                    <i class="icon-pencil"></i>&nbsp;&nbsp;Edit this Stakeholder
                </a>
            % else:
                <a href="${request.route_url('activities_read_one', output='form', uid=cstruct['id'])}">
                    <i class="icon-pencil"></i>&nbsp;&nbsp;Edit this deal
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
                <i class="icon-pencil"></i>&nbsp;&nbsp;Edit this Stakeholder
            </a>
        % else:
            <a href="${request.route_url('activities_read_one', output='form', uid=cstruct['id'])}">
                <i class="icon-pencil"></i>&nbsp;&nbsp;Edit this Deal
            </a>
        % endif
    </div>
% endif
