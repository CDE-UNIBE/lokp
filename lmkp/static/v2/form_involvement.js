/**
 * Function to remove a selected Involvement.
 */
function removeInvolvement(btn) {
    // Empty the values of all the readonly fields. Only reset those with an
    // id, others are used by Deform for mapping.
    var fieldset = $(btn).parent('p').parent('div');
    $.each(fieldset.find('input'), function() {
        if (this.id) {
            $(this).val(null);
        }
    });

    // Change the buttons back
    toggleInvolvementButtons(fieldset, false);

    return false;
}

function createSearch(inputId, tForUnknown, tForToomanyresults, tForNothingfound, queryUrl, searchPrefix, keys, rawKeys) {

    var inputField = $('#' + inputId);
    // This is the translated name key
    var nameKey = getKeyNames(keys)[0];
    // Not translated key name used to query the involvements
    var rawNameKey = getKeyNames(rawKeys)[0];
    var fieldset = inputField.parents().eq(5);

    // If there is an initial involvement, hide the "select"-button
    var emptyInvolvement = true;
    $.each(fieldset.find('input[readonly]'), function() {
        if ($(this).val() !== '') {
            emptyInvolvement = false;
        }
    });
    if (emptyInvolvement === false) {
        toggleInvolvementButtons(fieldset, true);
    }

    inputField.autocomplete({
        minLength: 4,
        // Use an ajax query as a search (by name). Query 11 results so the last
        // item can be replaced with a message to narrow down the search.
        source: function(request, response) {
            var ajaxData = {};
            ajaxData['limit'] = 11;
            // Use the raw i.e. English name key to query the database
            ajaxData[searchPrefix + '__' + rawNameKey + '__ilike'] = '%' + request.term + '%'
            $.ajax({
                url: queryUrl,
                dataType: 'json',
                data: ajaxData,
                success: function(data) {
                    if (data.total == 0) {
                        response(['nothingfound']);
                    } else {
                        // Find out which values of the stakeholder to display.
                        // Use the readonly fieldsets for this
                        var fields = [];
                        $.each(fieldset.find('input[readonly]'), function() {
                            fields.push($(this).attr('name'));
                        });
                        var results = $.map(data.data, function(item) {
                            // Get the values to display
                            var values = {};
                            for (var f in fields) {
                                values[fields[f]] = tForUnknown;
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
                            } else {
                                return null;
                            }
                        });
                        if (results.length == 11) {
                            results[11] = {label: 'toomanyresults'}
                        }
                        response(results);
                    }
                }
            });
        },
        // If an item is selected, set the content in the readonly involvement
        // representation and close the modal overview.
        select: function(event, ui) {
            if (ui.item.id && ui.item.version) {
                setInvolvementContent(inputField, ui.item);
                $('#formModalClose').trigger('click');
            }
        }
    }).data('autocomplete')._renderItem = function(ul, item) {
        if (item.id && item.version) {
            // Always use name as first display value
            var val1 = (nameKey in item) ? item[nameKey] : tForUnknown;
            // The second value is a composite of all other (non empty) display
            // values
            var val2 = [];
            for (var v in item) {
                if (v != 'label' && v != 'value' && v != nameKey
                    && v != 'id' && v != 'version' && item[v] != tForUnknown) {
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
                .append(tForNothingfound)
                .appendTo(ul);
        } else if (item.label == 'toomanyresults') {
            return $('<li class="shtoomanyresults">')
                .append(tForToomanyresults)
                .appendTo(ul);
        }
    };

}

function setInvolvementContent(inputField, involvementdata) {
    var fieldset = inputField.parents().eq(5);
    for (var d in involvementdata) {
        fieldset.find('input[name="' + d + '"]').val(involvementdata[d]);
    }
    toggleInvolvementButtons(fieldset, true);
}

function toggleInvolvementButtons(fieldset, hide) {
    if (hide === true) {
        fieldset.find('div.add-involvement').hide();
        fieldset.find('a.remove-involvement').show();
    } else {
        fieldset.find('a.remove-involvement').hide();
        fieldset.find('div.add-involvement').show();
    }
}
