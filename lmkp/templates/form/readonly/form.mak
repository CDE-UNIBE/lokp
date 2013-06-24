<%
    isStakeholder = 'itemType' in cstruct and cstruct['itemType'] == 'stakeholders'
%>

% if isStakeholder:
    <h3>Stakeholder Details</h3>
% else:
    <h3>Deal Details</h3>
% endif

% if 'id' in cstruct:
    <p class="id">${cstruct['id']}</p>
% endif

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

% if 'id' in cstruct:
    % if isStakeholder:
        <a href="/stakeholders/form/${cstruct['id']}">
            <i class="icon-pencil"></i>&nbsp;&nbsp;Edit this stakeholder
        </a>
    % else:
        <a href="/activities/form/${cstruct['id']}">
            <i class="icon-pencil"></i>&nbsp;&nbsp;Edit this deal
        </a>
    % endif
% endif