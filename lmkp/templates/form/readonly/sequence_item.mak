% if not field.widget.hidden:
    <li title="${field.description}">
        ${field.serialize(cstruct, readonly=True)}
    </li>
% endif