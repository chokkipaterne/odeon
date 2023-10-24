$(document).ready(function(){
  $("#country").on('change', function(e) {
     generate_states("country", "schstate");
  });
  generate_states("country", "schstate");
});
