<%

from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission

%>

% if isinstance(has_permission('administer', request.context, request), ACLAllowed):
<div>
    You are administrator!
</div>
% elif isinstance(has_permission('moderate', request.context, request), ACLAllowed):
<div>
    Wow, you're a moderator, that's a big responsibility
</div>
% elif isinstance(has_permission('edit', request.context, request), ACLAllowed):
<div>
    You have at least editor rights
</div>
% else:
<div>
    You are a public looser ...
</div>
% endif