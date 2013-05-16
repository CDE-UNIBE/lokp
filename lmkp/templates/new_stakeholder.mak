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
                $('input#shselectinput').autocomplete({
                    source: function(request, response) {
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
                                    var res = $.map(data.data, function(item) {
                                        var name = null;
                                        var country = '[Unknown]';
                                        var id = null;
                                        var version = null;
                                        if ('taggroups' in item) {
                                            $.each(item['taggroups'], function() {
                                                var tg = this;
                                                if ('tags' in tg) {
                                                    $.each(tg['tags'], function(){
                                                        var t = this;
                                                        if ('key' in t && 'value' in t) {
                                                            if (t['key'] == 'Name') {
                                                                name = t['value'];
                                                            }
                                                            if (t['key'] == 'Country of origin') {
                                                                country = t['value'];
                                                            }
                                                        }
                                                    });
                                                }
                                            });
                                        }
                                        id = item['id'];
                                        version = item['version'];
                                        if (name != null && id != null && version != null) {
                                            return {
                                                value: name,
                                                id: id,
                                                version: version,
                                                country: country
                                            }
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
                            setInvolvementContent(ui.item.id, ui.item.version,
                                ui.item.value, ui.item.country);
                            $('div#stakeholderformcontainer').hide();
                        }
                    },
                    minLength: 4
                }).data('autocomplete')._renderItem = function(ul, item) {
                    if (item.id && item.version) {
                        return $('<li>')
                            .data("item.autocomplete", item)
                            .append('<a>' + item.value
                                + '<br/><span class="shautocompletedescription">'
                                + item.country + '</span></a>')
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

            function setInvolvementContent(id, version, name, country) {
                var marker = $('span#currentlyactiveinstakeholderform');
                var fieldset = marker.parent('fieldset');
                fieldset.find('input[name=id]').val(id);
                fieldset.find('input[name=version]').val(version);
                fieldset.find('input[name=name]').val(name);
                fieldset.find('input[name=country]').val(country);
                fieldset.find('button.add-investor').hide();
                fieldset.find('button.edit-investor').show();
                fieldset.find('button.remove-investor').show();
            }

        </script>

    </body>
</html>


