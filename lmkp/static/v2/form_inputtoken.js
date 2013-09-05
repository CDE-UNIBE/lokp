/**
 * Add a new token to the list. Add it only if it does not yet exist.
 */
function addToken(oid, input, token) {
    var tokensDiv = input.siblings('div.tokenDiv');
    if (tokensDiv.length != 1) return;
    if (!findToken(tokensDiv, token)) {
        tokensDiv.append([
            '<div class="alert singleToken">',
            '<button type="button" class="close" data-dismiss="alert">&times;</button>',
            '<input class="hide" name="' + oid + '" type="checkbox" value="' + token + '" checked="checked"/>',
            '<div class="tokenName">' + token + '</div>',
            '</div>'
        ].join(''));
    }
}

/**
 * Check if a given token exists with a div of tokens.
 */
function findToken(tokenDiv, token) {
    var found = false;
    $.each(tokenDiv.find('.tokenName'), function() {
        if ($.trim($(this).text()) == token) {
            found = true;
        }
    });
    return found;
}

$(document).ready(function() {
    // Initialize the tooltips
    $('.inputTokenHelp').tooltip({html: true});
});