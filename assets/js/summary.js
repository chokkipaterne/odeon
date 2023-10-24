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

  $('#datefrom').datepicker({
    "format":'yyyy-mm-dd',
    "autoClose":true,
    "defaultDate": new Date($('#datefrom').val()),
      onClose: function () {
        $("#search-form").submit();
      }
  });
  $('#dateto').datepicker({
    "format":'yyyy-mm-dd',
    "autoClose":true,
    "defaultDate": new Date($('#datefrom').val()),
      onClose: function () {
        $("#search-form").submit();
      }
  });

  $("#country").change(function() {
    $("#search-form").submit();
  });

  $("#country").on('change', function(e) {
     generate_states("country", "state");
  });
  generate_states("country", "state");
  $('#state').keypress(function(event){
      var keycode = (event.keyCode ? event.keyCode : event.which);
      if(keycode == '13'){
        $("#search-form").submit();
      }
      //Stop the event from propogation to other handlers
      //If this line will be removed, then keypress event handler attached
      //at document level will also be triggered
      event.stopPropagation();
  });
});
