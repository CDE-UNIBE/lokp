/**
 *
 */

$(function() {
    $('.update_option_in_overview').each(function() {
        update_option_overview_value($(this).attr('id'));
    });
    $('.update_option_in_overview').change(function() {
        update_option_overview_value($(this).attr('id'));
    });
    $('.update_checkbox_in_overview').each(function() {
        update_checkbox_overview_value($(this).attr('id'));
    });
    $('.update_checkbox_in_overview').change(function() {
        update_checkbox_overview_value($(this).attr('id'));
    });
});

function update_option_overview_value(id) {
    var el = $('#' + id + ' option:selected');
    if (el.length) {
        $('#' + id + '_overview').text(el.text());
    }
}

function update_checkbox_overview_value(div_id) {
    var selected = [];
    $('#' + div_id + ' input:checked').each(function() {
        var label = $(this).parent('label');
        if (label.length) {
            selected.push($.trim(label.text()));
        }
    });
    var all = $('#' + div_id + ' input');
    if (all.length == selected.length) {
        var html = translation_all;
    } else {
        html = selected.join('<br/>');
    }
    $('#' + div_id + '_overview').html(html)
}
