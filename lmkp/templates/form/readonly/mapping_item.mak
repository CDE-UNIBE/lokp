<%
    # Leave out all fields which contain no values!
    from lmkp.views.form import structHasOnlyNullValues
    showfield = not structHasOnlyNullValues(cstruct)
%>

% if showfield:
    <li title="${field.description}">
        <p class="desc"
           title="${field.description}"
        >${field.title}</p>
    ${field.serialize(cstruct, readonly=True)}
    </li>
% endif