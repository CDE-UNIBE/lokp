<%
    import colander
%>
% for i, tup in enumerate(subfields):

    <%
        change = 'change' in tup[0] and tup[0]['change'] != colander.null
        cls = 'span6 taggroup-content'
        if change:
            cls += ' change'
    %>

    % if i > 0:
            </div>
        </div>
        <div class="row-fluid">
            <div class="span9 grid-area">
    % endif
    <div class="${cls}">
        ${field.render_template(field.widget.readonly_item_template, field=tup[1], cstruct=tup[0])}
    </div>
% endfor