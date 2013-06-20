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