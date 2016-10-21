/**
 * The functionality when clicking a table row.
 * Shows a popup on the same line as the selected row with a link to show the
 * other side of the involvements.
 * On small screens, the popup appears on top of the selected row.
 */
$('#itemgrid tbody>tr').tooltip({
  html: true,
  placement: function(tip, element) {
    var padding_right = $('.item-grid-wrapper').css('padding-right')
      .replace("px", "");
    if (padding_right > 20) {
      return 'right';
    }
    return "top";
  },
  title: '<a href="#">' + link_involvement_text + '</a>',
  trigger: 'manual'
});
$('#itemgrid tbody>tr').on('click', function() {
  var identifier = $(this).find('td.identifier').html();
  if (!identifier) return;
  var itemType = $(this).find('td.itemType').html();
  if (!itemType) return;
  var other = (itemType == 'stakeholders') ? 'activities' : 'stakeholders';
  var by = (itemType == 'stakeholders') ? 'bystakeholders' : 'byactivities';
  var url = '/' + [other, by, 'html', identifier].join('/');
  window.location.href = url;

  /*$('#itemgrid tbody>tr').not(this).tooltip('hide');
  $(this).tooltip('toggle');
  $('.tooltip a').attr('href', url);*/
});

$(window).resize(function() {
  $('#itemgrid tbody>tr').tooltip('hide');
});
