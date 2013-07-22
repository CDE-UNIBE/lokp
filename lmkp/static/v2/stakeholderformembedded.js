/**
 * Necessary variables with translated text for this file (must be defined and
 * translated in template):
 * tForUnknown
 * tForNothingfound
 * tForToomanyresults
 */

$(function() {

    var nameKey = getKeyNames(shKeys)[0];

    $('#shselectinput').autocomplete({
        minLength: 2,
        // Use an ajax query as a search (by name). Query 11 results so the last
        // item can be replaced with a message to narrow down the search.
        source: function(request, response) {
            $.ajax({
                url: queryUrl,
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
                        // Find out which values of the stakeholder to display.
                        // Use the readonly fieldsets for this
                        var marker = $('#currentlyactiveinstakeholderform');
                        var fieldset = marker.parent('div');
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
                setInvolvementContent(ui.item);
                $('#formModalClose').trigger('click');
            }
        }
    }).data('autocomplete')._renderItem = function(ul, item) {
        if (item.id && item.version) {
            // Always use name as first display value
            var val1 = (nameKey in item) ? item[nameKey] : tForUnknown;
            // The second value is a composite of all other (non
            // empty) display values
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
});

function createNewStakeholder() {
    $('div#create-new-stakeholder').show();
    $('div#select-stakeholder').hide();
    return false;
}

function setInvolvementContent(involvementdata) {
    var marker = $('#currentlyactiveinstakeholderform');
    var fieldset = marker.parent('div');
    for (var d in involvementdata) {
        fieldset.find('input[name="' + d + '"]').val(involvementdata[d]);
    }
    fieldset.find('a.add-stakeholder').hide();
    fieldset.find('a.remove-stakeholder').show();
}

function showLoadingIndicator(btn) {
    var form = $(btn).closest('form');
    form.hide();
    var loading = $('#stakeholderFormLoading');
    loading.show();
}