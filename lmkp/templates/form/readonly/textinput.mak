% if field.name == 'URL / Web':
<p class="truncate ttip" data-toggle="tooltip" title="${_('Open the link in a new window')}">
    % if not cstruct.startswith('http://'):
        <a href="http://${cstruct}" target="_blank">${cstruct}</a>
    % else:
        <a href="${cstruct}" target="_blank">${cstruct}</a>
    % endif
</p>
% else:
    ${cstruct}
    % if helptext:
        (${helptext})
    % endif
% endif
