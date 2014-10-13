% if field.name == 'URL / Web':
<p class="truncate ttip" data-toggle="tooltip" title="${_('Open the link in a new window')}">
    <a href="${cstruct}" target="_blank">${cstruct}</a>
</p>
% else:
    ${cstruct}
    % if helptext:
        (${helptext})
    % endif
% endif
