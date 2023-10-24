$(document).ready(function() {
  $('#search').keypress(function(event){
      var keycode = (event.keyCode ? event.keyCode : event.which);
      if(keycode == '13'){
        $("#search-form").submit();
      }
      //Stop the event from propogation to other handlers
      //If this line will be removed, then keypress event handler attached
      //at document level will also be triggered
      event.stopPropagation();
  });
  //generate_states("reqcountry", "reqstate");
  //generate_states("dtcountry", "dtstate");
});
$(document).ready(function(){
  $('.tabs').tabs();
  $("#country").on('change', function(e) {
     generate_states("country", "schstate");
  });
  generate_states("country", "schstate");
});
