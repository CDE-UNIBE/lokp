$(function() {
    var filterCounter = 0;

    /**
     * Functionality when clicking the link to open/close the filter area.
     */
    $('.filter_area_openclose').click(function() {
        $('.filter_area').slideToggle();
        filterCounter++;

        // closed
        if (filterCounter % 2 == 0) {
            $(this).find('span').show();
            $(this).find('i').removeClass().addClass('icon-double-angle-down pointer');
            $(this).css('border-top', 'none');
        }

        // openend
        else {
            $(this).find('span').hide();
            $(this).find('i').removeClass().addClass('icon-double-angle-up pointer');
            $(this).css('border-top', 'double 3px #BDBDBD');
        }
    });
});