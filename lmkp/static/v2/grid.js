/**
 * The functionality when clicking a table row.
 * Shows a popup on the same line as the selected row.
 */
$('#activitygrid tbody>tr').click(function() {
    $(this).parent().find('tr').removeClass('active-row');
    $(this).addClass('active-row');

    var identifier = $(this).find('td.identifier').html();
    if (!identifier) return;

    if ($('div.show-investors.visible-phone').is(':visible')) {
        // Switch directly
        // TODO
        console.log("switch");
    } else {
        var popup = $('.show-investors-wrapper');
        var position = $(this).position().top - $('#activitygrid').position().top - 5;
        popup.removeClass('hidden').css({'margin-top': position});

        var l = popup.find('a').attr('href', '/stakeholders/grid');
    }
});
