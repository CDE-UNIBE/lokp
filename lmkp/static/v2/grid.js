/**
 * The functionality when clicking a table row.
 * Shows a popup on the same line as the selected row.
 */
$('#activitygrid tbody>tr').click(function() {
    $(this).parent().find('tr').removeClass('active-row');
    $(this).addClass('active-row');
    var popup = $('.show-investors-wrapper');
    popup.removeClass('hidden').css({'top': $(this).position().top});
});
