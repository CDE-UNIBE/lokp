<%
from lmkp.views.translation import get_profiles
profiles = get_profiles()
%>

<h3>The landing page!</h3>

Select a profile:
% for p in profiles:
    <p><a href="/${p[0]}">${p[0]}</a></p>
% endfor

