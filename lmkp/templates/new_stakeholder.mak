<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>

        <%
            if 'scripts/jquery-ui-1.8.11.custom.min.js' not in js_links:
                js_links.append('scripts/jquery-ui-1.8.11.custom.min.js')
        %>

        % for reqt in js_links:
            <script type="text/javascript" src="/formstatic/${reqt}"></script>
        % endfor
    </head>

    <body>

        <div id="new-stakeholder-buttons">
            <button id="create-new-stakeholder">
                <span>Create a new Stakeholder</span>
            </button>
            <button id="select-existing-stakeholder">
                <span>Select an existing Stakeholder</span>
            </button>
        </div>

        <div id="create-new-stakeholder">
            ${form | n}
        </div>

        <div id="select-existing-stakeholder">
            <p>Start typing (at least 4 characters) to search a Stakeholder by name.</p>
            <input type="text" id="shselectinput"/>
        </div>

        <script type="text/javascript">
            deform.load();

            $('button#create-new-stakeholder').click(function() {
                hideButtons();
                $('div#create-new-stakeholder').show();
            });

            $('button#select-existing-stakeholder').click(function() {
                hideButtons();
                // TODO: Translation
                var unknownString = 'Unknown';
                $('input#shselectinput').autocomplete({
                    source: function(request, response) {
                        // Use an ajax query as a search (by name). Query 11
                        // results so the last item can be replaced with a
                        // message to narrow down the search.
                        $.ajax({
                            url: '/stakeholders/json',
                            dataType: 'json',
                            data: {
                                sh__queryable: 'Name',
                                sh__Name__ilike: request.term,
                                limit: 11
                            },
                            success: function(data) {
                                if (data.total == 0) {
                                    response(['nothingfound']);
                                } else {
                                    // Find out which values of the stakeholder
                                    // to display (the readonly fieldsets)
                                    var marker = $('span#currentlyactiveinstakeholderform');
                                    var fieldset = marker.parent('fieldset');
                                    var fields = []
                                    $.each(fieldset.find('input.readonly'), function() {
                                        fields.push($(this).attr('name'));
                                    });
                                    var res = $.map(data.data, function(item) {
                                        // Get the values to display
                                        var values = {};
                                        for (var f in fields) {
                                            values[fields[f]] = unknownString;
                                        }
                                        if ('taggroups' in item) {
                                            $.each(item['taggroups'], function() {
                                                var tg = this;
                                                if ('tags' in tg) {
                                                    $.each(tg['tags'], function(){
                                                        var t = this;
                                                        if ('key' in t && 'value' in t) {
                                                            for (var v in values) {
                                                                if (t['key'] == v) {
                                                                    values[v] = t['value'];
                                                                }
                                                            }
                                                        }
                                                    });
                                                }
                                            });
                                        }
                                        values['id'] = item['id'];
                                        values['version'] = item['version'];
                                        if (values['id'] != null && values['version'] != null) {
                                            return values
                                        }
                                    });
                                    if (res.length == 11) {
                                        res[11] = {label: 'toomanyresults'}
                                    }
                                    response(res);
                                }
                            }
                        });
                    },
                    select: function(event, ui) {
                        if (ui.item.id && ui.item.version) {
                            setInvolvementContent(ui.item);
                            $('div#stakeholderformcontainer').hide();
                        }
                    },
                    minLength: 4
                }).data('autocomplete')._renderItem = function(ul, item) {
                    if (item.id && item.version) {
                        // Always use name as first display value
                        var val1 = ('Name' in item) ? item.Name : unknownString;
                        // The second value is a composite of all other (non
                        // empty) display values
                        var val2 = [];
                        for (var v in item) {
                            if (v != 'label' && v != 'value' && v != 'Name'
                                && v != 'id' && v != 'version' && item[v] != unknownString) {
                                val2.push(item[v]);
                            }
                        }
                        return $('<li>')
                            .data("item.autocomplete", item)
                            .append('<a>' + val1
                                + '<br/><span class="shautocompletedescription">'
                                + val2.join(' - ') + '</span></a>')
                            .appendTo(ul);
                    } else if (item.label == 'nothingfound') {
                        return $('<li class="shnothingfound">')
                            .append('No results found.')
                            .appendTo(ul);
                    } else if (item.label == 'toomanyresults') {
                        return $('<li class="shtoomanyresults">')
                            .append('Too many results to display. Try to enter more characters')
                            .appendTo(ul);
                    }
                };
                $('div#select-existing-stakeholder').show();
            });

            function hideButtons() {
                $('div#new-stakeholder-buttons').hide();
            }

            function setInvolvementContent(involvementdata) {
                var marker = $('span#currentlyactiveinstakeholderform');
                var fieldset = marker.parent('fieldset');
                for (var d in involvementdata) {
                    fieldset.find('input[name="' + d + '"]').val(involvementdata[d]);
                }
                fieldset.find('button.add-investor').hide();
                fieldset.find('button.edit-investor').show();
                fieldset.find('button.remove-investor').show();
            }

        </script>

    </body>
</html>


