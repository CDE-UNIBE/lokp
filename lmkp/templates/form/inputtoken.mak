${field.start_sequence()}

<div class="row-fluid">
    <div class="span4">
        <label for="${field.oid}">
            % if field.title:
                ${field.title}
            % elif field.name:
                ${field.name}
            % endif
        </label>
        % if field.required:
            <span class="required-form-field"></span>
        % elif desired:
            <span class="desired-form-field"></span>
        % endif
    </div>
    <div class="span8">
        <input id="input-${field.oid}" class="input-style inputToken" type="text" data-provide="typeahead" autocomplete="off">
        <span class="inputTokenHelp icon-question-sign" data-toggle="tooltip" title="${_('Start typing in the textfield to search and select values.')}"></span>
        <div class="tokenDiv">
            % for c in cstruct:
                % if len(c.split('|')) == 2:
                    <div class="alert singleToken">
                        <button type="button" class="close" data-dismiss="alert">&times;</button>
                        <input class="hide" name="${field.oid}" type="checkbox" value="${c}" checked="checked"/>
                        <div class="tokenName">
                            ${c.split('|')[1]}
                        </div>
                    </div>
                % endif
            % endfor
        </div>
    </div>
</div>

<script type="text/javascript">
    deform.addCallback(
        '${field.oid}',
        function(oid) {
            var input = $('#input-' + oid);
            var values = [
                % for index, choice in enumerate(values):
                    '${choice[1]}',
                % endfor
            ];
            input.typeahead({
                source: values,
                updater: function(item) {
                    addToken(oid, input, item);
                }
            });
        }
    );
</script>

${field.end_sequence()}
