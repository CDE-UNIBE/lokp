<%
    import colander
%>
% for i, tup in enumerate(subfields):

    <%
        change = 'change' in tup[0] and tup[0]['change'] != colander.null
        cls = 'span6 taggroup-content deal-moderate-col'
        if change:
            cls += ' change'
    %>

    % if i > 0:
        </div>
        <div class="row-fluid deal-moderate-col-wrap">
            <div class="${cls}"></div>
    % endif
    <div class="${cls}">
        ${field.render_template(field.widget.readonly_item_template, field=tup[1], cstruct=tup[0])}
    </div>
% endfor