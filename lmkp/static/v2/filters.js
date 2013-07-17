// This object is used to map the filter operators used for display and the ones
// submitted in the query.
var filterOperators = {
    'predefined': [
        ['=', 'like'],
        ['!=', 'nlike']
    ],
    'text': [
        ['=', 'ilike'],
        ['!=', 'nlike']
    ],
    'number': [
        ['=', 'eq'],
        ['!=', 'ne'],
        ['<', 'lt'],
        ['<=', 'lte'],
        ['>', 'gt'],
        ['>=', 'gte']
    ]
}

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

    // Initial operators: Text
    var operators = filterOperators.text;
    _addOperators(operators);

    // Open filter area if there is at least one active filter.
    if ($('.active-filter').length) {
        $('.filter_area_openclose').click();
    }
});

/**
 * Function called when selecting a new key in the dropdown. Puts the translated
 * value in the display field, sets the internal value, changes the available
 * filter operators and the key field (populates it if there are predefined
 * values).
 */
function selectKey(keyTranslated, keyName, keyType, itemType) {

    // Set the value of the selected key in the field.
    $('#new-filter-key').val(keyTranslated);
    $('#new-filter-key-internal').val(keyName);

    /**
     * TODO: Make this more dynamic (consider the following use case: A user
     * selects a SH key and then start typing an A key).
     */
    $('#new-filter-itemtype').val(itemType);

    // Update the value field.
    if (keyType != 'dropdown' && keyType != 'checkbox') {
        $('#new-filter-value-box').replaceWith('<div id="new-filter-value-box" class="btn-group"><input id="new-filter-value-internal" type="text" class="filter-value" placeholder="Value" /></div>');
    } else {
        $('#new-filter-value-box').replaceWith('<div id="new-filter-value-box" class="btn-group input-append"><input id="new-filter-value" class="select-value" type="text" placeholder="Value" /><button class="btn select_btn_filter_right dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button><input id="new-filter-value-internal" type="hidden" value=""/></div>');
        $.get('/json/filtervalues', {
            type: itemType,
            key: keyName
        }, function(data) {
            var menu = $('<ul class="dropdown-menu pull-right" role="menu"></ul>');
            $.each(data, function(i, d) {
                menu.append('<li><a href="#" onClick="javascript:selectValue(\'' + d[0] + '\', \'' + d[1] + '\')">' + d[0] + '</a></li>')
            });
            $('#new-filter-value-box').append(menu);
        });
    }

    // Update the operator field.
    var operators = filterOperators.number;
    if (keyType == 'dropdown' || keyType == 'checkbox') {
        operators = filterOperators.predefined;
    } else if (keyType == 'text' || keyType == 'string') {
        operators = filterOperators.text;
    }
    _addOperators(operators);

    return false;
}

/**
 * Function called when selecting a new operator in the dropdown. Puts the value
 * in the display field.
 */
function selectOperator(display, operator) {
    $('#new-filter-operator-display').html(display);
    $('#new-filter-operator').val(operator);
}

/**
 * Function called when selecting a new value in the dropdown. Puts the
 * translated value in the display field and sets the internal value.
 */
function selectValue(valueTranslated, valueName) {
    $('#new-filter-value').val(valueTranslated);
    $('#new-filter-value-internal').val(valueName);
}

/**
 * Function to add a new filter. Collects the values from the form and prepares
 * it to add it as a query parameter.
 */
function addNewFilter() {

    // Collect the values
    var key = $('#new-filter-key-internal').val();
    var value = $('#new-filter-value-internal').val();
    var itemtype = $('#new-filter-itemtype').val()
    var operator = $('#new-filter-operator').val();

    if (key && value && operator) {
        // Prepare the query string as object
        var filterstring = itemtype + '__' + key + '__' + operator;
        var filter = {}
        filter[filterstring] = value;
        addQueryParam(filter);
    }
}

/**
 * Function to delete an active filter with a given id.
 */
function deleteFilter(id) {
    var filterstring = $('#active-filter-' + id).val();
    removeQueryParam(filterstring);
}

/**
 * Function to add an object as a string to the query parameter.
 */
function addQueryParam(paramobject) {
    // Collect all current query parameters
    var params = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');

    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        if (hash[1]) {
            params.push([hash[0], hash[1].replace('#', '')]);
        }
    }

    // Update or set the ones provided
    for (var o in paramobject) {
        params.push([o, encodeURIComponent(paramobject[o])]);
    }

    // Create a query string with all parameters and redirect to new URL
    var ps = [];
    $.each(params, function(i, d) {
        ps.push(d[0] + '=' + d[1]);
    });
    location.href = '?' + ps.join('&');
}

/**
 * Function to remove a parameter from the query string.
 */
function removeQueryParam(paramstring) {
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    var newHashes = []
    $.each(hashes, function(i, h) {
        // Remove any '#' in the URL
        var newHash = h.replace('#', '');
        if (_urldecode(newHash) != _urldecode(paramstring)) {
            newHashes.push(newHash);
        }
    });
    location.href = '?' + newHashes.join('&');
}

/**
 * Function to populate the dropdown with the filter operators.
 */
function _addOperators(operators) {
    var operatorDropdown = $('#new-filter-operator-dropdown');
    // Remove previous operators from dropdown
    operatorDropdown.empty();
    // Populate dropdown
    $.each(operators, function(i, o) {
        if (i == 0) {
            // Set the first operator
            $('#new-filter-operator-display').html(operators[0][0]);
            $('#new-filter-operator').val(operators[0][1]);
        }
        operatorDropdown.append('<li><a href="#" onClick="javascript:selectOperator(\'' + o[0] + '\', \'' + o[1] + '\')">' + o[0] + '</a></li>');
    });
}

/**
 * Helper function to decode a string, also handles spaces being decoded as +.
 * http://stackoverflow.com/a/4458580/841644
 */
function _urldecode(str) {
   return decodeURIComponent((str+'').replace(/\+/g, '%20'));
}