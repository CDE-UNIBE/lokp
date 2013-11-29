% if not field.widget.hidden:
    ${field.serialize(cstruct, readonly=True)}
% endif