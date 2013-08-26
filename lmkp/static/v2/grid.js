/**
 * The functionality when clicking a table row.
 * Shows a popup on the same line as the selected row with a link to show the
 * other side of the involvements.
 * On small screens, clicking the row triggers the link directly.
 */
$('#activitygrid tbody>tr').click(function() {
    $(this).parent().find('tr').removeClass('active-row');
    $(this).addClass('active-row');

    var identifier = $(this).find('td.identifier').html();
    if (!identifier) return;

    var itemType = $(this).find('td.itemType').html();
    if (!itemType) return;

    var otherType = (itemType == 'stakeholders') ? 'activities' : 'stakeholders';
    var byThis = (itemType == 'stakeholders') ? 'bystakeholders' : 'byactivities';
    var url = '/' + [otherType, byThis, 'html', identifier].join('/');

    if ($('div.show-investors.visible-phone').is(':visible')) {
        // Switch directly
        window.location.replace(url);
    } else {
        // Show a popup
        var popup = $('.show-investors-wrapper');
        var position = $(this).position().top - $('#activitygrid').position().top - 5;
        popup.removeClass('hidden').css({'margin-top': position});
        popup.find('a').attr('href', url);
    }
});
