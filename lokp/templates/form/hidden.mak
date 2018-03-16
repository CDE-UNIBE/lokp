<%
    from pyramid.compat import escape
%>

<input type="hidden"
       name="${field.name}"
       value="${escape(cstruct)}"
       id="${field.oid}"
/>

## ${cstruct}