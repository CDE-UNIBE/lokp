<%
    import colander
%>
% for i, tup in enumerate(subfields):

    <%
        change = 'change' in tup[0] and tup[0]['change'] != colander.null
        cls = 'span6 taggroup-content deal-moderate-col'
        if len(subfields) == 1:
            cls = 'row-fluid taggroup-content deal-moderate-col'
        else:
            cls = 'row-fluid taggroup-content deal-moderate-col-wrap'
        if change:
            cls += ' change'
    %>

    <div class="${cls}">
        ${field.render_template(field.widget.readonly_item_template, field=tup[1], cstruct=tup[0])}
    </div>
% endfor