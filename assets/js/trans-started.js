$(function () {
  $("#country").on('change', function(e) {
     generate_states("country", "trans_state");
  });
  $("#country").trigger('change');
});

$(document).ready(function(){
  $('.settopic').formSelect();
});
