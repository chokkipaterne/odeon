var instance_tabs = ""

//Show and hide project description
function togglepdesc(pid){
  $("#pdesc1_"+pid).toggleClass("hide");
  $("#pdesc2_"+pid).toggleClass("hide");
}

function initcomment(parent="", id=""){
  if(parent != ""){
    var feed = $("#feed"+id).html().trim();
    $("#replycomment").html("<br/>"+feed);
    $("#replyp").removeClass("hide");
    $("#parent_feedback").val(parent);
    $("#feedback_type").val("general");
    $("#rating").addClass("hide");
    $("#rate").val("");

    $("#fdstatus").attr('required', false);
    $("#feedpjstatus").addClass("hide");
    $("#fdstatus").val("");
    //$("#feedback_type_div").addClass("hide");
  }else{
    $("#replycomment").html("");
    $("#replyp").addClass("hide");
    $("#parent_feedback").val("");
    $("#comment").val("");
    tab_show_callback();
    //$("#feedback_type_div").removeClass("hide");
    //$("#feedback_type").val("general");
  }
  $('html,body').animate({
  scrollTop: $("#feedback-form").offset().top-60},
  'slow');
}

function activetabs(goto, tabactive){
  if(goto != ""){
    if($("#"+goto).length){
      $('html,body').animate({
        scrollTop: $("#"+goto).offset().top-40},
      'slow');
    }
  }
  $('.tabs').tabs('select',tabactive);
}

function tab_show_callback(){
	//console.log('showing tab +++++ ' + instance_tabs.index)
  index = instance_tabs.index;
  $("#fdstatus").attr('required', false);
  $("#feedpjstatus").addClass("hide");
  $("#parent_feedback").val("");
  $("#replyp").addClass("hide");
  $("#fdstatus").val("");
  $("#rating").addClass("hide");
  $("#rate").val("");

  if(index == 0){
    $("#postcomment").text(gettext("Refine needs for project"));
    $("#feedback_type").val("requirement");
  }
  if(index == 1){
    $("#fdstatus").attr('required', true);
    $("#feedpjstatus").removeClass("hide");
    $("#postcomment").text(gettext("Inform users of the progress of the project's development"));
    $("#feedback_type").val("status");
  }
  if(index == 2){
    $("#postcomment").text(gettext("Add comment to improve the developed project"));
    $("#feedback_type").val("general");
    $("#rating").removeClass("hide");
    $('.starrr').starrr({
      max: 5,
      change: function(e, value){
        $("#rate").val(value);
      }
    });
  }
}

$(document).ready(function() {
  //$('.tabs').tabs();
  $("#feedback_filter_type").on('change', function(e) {
    var val = $("#feedback_filter_type").val();
    if(val == ""){
      $(".feedli").removeClass("hide");
    }else{
      $(".feedli").addClass("hide");
      $("."+val).removeClass("hide");
    }
  });

  for (let i = 1; i < 6; i++) {
    $('.starrr'+i).starrr({
      readOnly: true,
      rating: parseInt(i)
    });
  }

  var elem = $('.tabs')
  var options = {onShow: tab_show_callback}
  var init_tabs = M.Tabs.init(elem, options);
  instance_tabs = M.Tabs.getInstance(elem);
  tab_show_callback();

});
