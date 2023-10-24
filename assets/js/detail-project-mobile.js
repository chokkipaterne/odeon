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
  $("#addcomment").addClass("hide");
  $("#rating").addClass("hide");
  $("#rate").val("");

  if(index == 0){
  }
  if(index == 1){
  }
  if(index == 2){
    $("#addcomment").removeClass("hide");
    $("#postcomment").text(gettext("Add comment to improve this app"));
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

function savelink(action_type){
  $("#action_type").val(action_type);
  var $form = $("#savelike-form"),
  url = $form.attr("action");
  mydata = $form.serialize();
  var nb_likes = 0;
  var nb_favorites = 0;
  if(action_type != "like"){
    nb_favorites = $("#nb_favorites").html();
    nb_favorites = nb_favorites.trim();
    nb_favorites = parseInt(nb_favorites);
  }else{
    nb_likes = $("#nb_likes").html();
    nb_likes = nb_likes.trim();
    nb_likes = parseInt(nb_likes);
  }
  var like_type = $("#like_type").val();

  var savelikeForm = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(resultData) {
        if(action_type == "like"){
          if (resultData.success) {
            nb_likes = nb_likes + 1;
            $("#nb_likes").html(nb_likes);
            if(like_type == "project"){
              M.toast({html: gettext("Thank for supporting this project"), classes: 'green rounded', displayLength:2000});
            }else{
              M.toast({html: gettext("Thank for supporting this dataset"), classes: 'green rounded', displayLength:2000});
            }
          }else{
            if(like_type == "project"){
              M.toast({html: gettext("It seems that you already like this project."), classes: 'red rounded', displayLength:10000});
            }else{
              M.toast({html: gettext("It seems that you already like this dataset."), classes: 'red rounded', displayLength:10000});
            }
          }
          $("#msglike").addClass("hide");
        }else{
          if (resultData.success) {
            nb_favorites = nb_favorites + 1;
            $("#nb_favorites").html(nb_favorites);
            $("#btnrmfav").removeClass("hide");
            $("#btnaddfav").addClass("hide");
            if(like_type == "project"){
              M.toast({html: gettext("Add to favorites successfully."), classes: 'green rounded', displayLength:2000});
            }
          }else{
            nb_favorites = nb_favorites - 1;
            $("#nb_favorites").html(nb_favorites);
            $("#btnrmfav").addClass("hide");
            $("#btnaddfav").removeClass("hide");
            if(like_type == "project"){
              M.toast({html: gettext("Remove from favorites successfully."), classes: 'red rounded', displayLength:2000});
            }
          }
        }
      },
      error:function(err) {
      },
  });
}
//Handle share project or file button
function share_info(dash_code="", file_code=""){
  //$("#dash_code").val("");
  weblink = $("#initweblink").val();
  if(file_code == ""){
    $("#message").val(gettext("Hi, you might be interested in the following project: ")+weblink+"detail-project/"+dash_code+"/");
  }else{
    $("#message").val(gettext("Hi, you might be interested in the following dataset: ")+weblink+"explore-data/"+dash_code+"/"+file_code+"/");
  }

  var elem = document.querySelectorAll('#modalShare')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}

$(document).ready(function() {
  $('#modalShare').modal();

  /*Button to share projet to a friend*/
  $(".modal-share").click(function() {
    var $form = $("#share-form"),
    url = $form.attr("action");
    mydata = $form.serialize();
    $(".modal-share").attr('disabled', true);
    var shareProj = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          $(".modal-share").attr('disabled', false);
          if (resultData.success) {
            $("#emails").val("");
            var elem = document.querySelectorAll('#modalShare')[0];
            var instance = M.Modal.getInstance(elem);
            instance.close();
            M.toast({html: resultData.message, classes: 'green rounded', displayLength:2000});
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
        },
        error:function(err) {
          $(".modal-share").attr('disabled', false);
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
    });
  });
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
