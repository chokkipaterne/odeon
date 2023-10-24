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
  show_hide();
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

  $("#type").change(function() {
    $("#search-form").submit();
  });
  $("#status").change(function() {
    $("#search-form").submit();
  });

  $("#country").change(function() {
    $("#search-form").submit();
  });

  $("#sort").change(function() {
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

function update_topic(id, name){
  if ($("#theme"+id).hasClass("active")){
    $("#topic").val("");
  }else{
    $("#topic").val(name);
  }
  $("#search-form").submit();
}

//Show more options
function showmore(){
  $(".schmore").removeClass("hide");
  $(".schless").addClass("hide");
}

//Show less options
function showless(){
  $(".schmore").addClass("hide");
  $(".schless").removeClass("hide");
}

//Show or hide options in select based on project type
function show_hide(){
  var proj_type = $("#type").val();
  if (proj_type == "proposed"){
    $(".opths").addClass("hide");
    $(".sp").removeClass("hide");
  }else if (proj_type != "proposed"){
    $(".opths").addClass("hide");
    $(".ep").removeClass("hide");
  }
}
