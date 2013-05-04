% if not field.widget.hidden:
<li 
    % if field.error and field.widget.error_class:
        class="field ${field.widget.error_class}"
    % else:
        class="field"
    % endif
    title="${field.description}"
    id="item-${field.oid}"
    i18n:domain="deform"
>

    <!-- mapping_item -->
    % if not field.widget.category == 'structural':
        <label class="desc"
               title="${field.description}"
               for="${field.oid}"
        >
            ${field.title}

            % if field.required:
                <span class="req"
                      id="req-${field.oid}"
                >*</span>
            % endif

        </label>
    % endif

    ${field.serialize(cstruct)}

    % if field.error:
        <%
            errstr = 'error-%s' % field.oid
        %>
        % for msg in field.error.messages():
            <p
                % if msg.index==0:
                    id="${errstr}"
                % else:
                    id="${'%s-%s' % (errstr, msg.index)}"
                % endif
                class="${field.widget.error_class}"
                i18n:translate=""
            >${msg}</p>
        % endfor
    % endif

    <!-- /mapping_item -->
    
</li>
% endif