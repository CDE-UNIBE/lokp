$("#profile-select").change(function(event){
    console.log("here");
    var p = event.target.value;
    var currentUrl = window.location.href.split("?")[0];
    window.location.href = currentUrl + "?_PROFILE_=" + p;
});

$("#language-select").change(function(event){
    var p = event.target.value;
    var currentUrl = window.location.href.split("?")[0];
    window.location.href = currentUrl + "?_LOCALE_=" + p;
});

/**
 * Function to update certain query parameters (passed as dict-like object)
 * without modifying other existing query parameters.
 */
function updateQueryParams(paramobject) {
    // Collect all current query parameters
    var params = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        if (hash[1]) {
           params[hash[0]] = hash[1];
        }
    }

    // Update or set the ones provided
    for (var o in paramobject) {
        params[o] = encodeURIComponent(paramobject[o]);
    }

    // Create a query string with all parameters and redirect to new URL
    var ps = [];
    for (var p in params) {
        ps.push(p + '=' + params[p]);
    }
    location.href = '?' + ps.join('&');
}
