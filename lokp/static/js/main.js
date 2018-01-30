/**
 * Function to get the key names used for the overview representation of an
 * Activity or a Stakeholder. If the keys are ordered with numbers, return the
 * names of the keys in that order.
 * Returns an array with the names of the keys.
 */
function getKeyNames(keys) {
    var names = [];
    $.each(keys, function() {
        if ($.isNumeric(this[1])) {
            names[this[1]] = this[0];
        } else {
            names.push(this[0]);
        }
    });
    return $.grep(names, function(n) { return(n) });
}
