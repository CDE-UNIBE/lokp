% if field.name == 'URL / Web':
<p class="truncate tooltipped" data-tooltip="${_('Open the link in a new window')}">
    % if not cstruct.startswith('http://') and not cstruct.startswith('https://'):
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
