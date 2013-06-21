/**
 * Functionality when clicking the link to open/close the filter area.
 */
$('.filter_area_openclose').click(function() {
    var filterarea = $('.filter_area');
    if (filterarea.is(':visible')) {
        filterarea.hide();
        $(this).find('i').removeClass().addClass('icon-double-angle-down pointer');
    } else {
        filterarea.show();
        $(this).find('i').removeClass().addClass('icon-double-angle-up pointer');
    }
});
