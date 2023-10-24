$(document).ready(function() {
  $("#col").select2();
  //Handle when user changes column for data exploration
  $('#col').change(function() {
    var val = $("#col").val();

    if(val != ""){
      id = "div_"+val
      if($("#"+id).length){
        $('html, body').animate({
            scrollTop: $("#"+id).offset().top-40
        }, 2000);
      }else{
        var $form = $("#explore-form");
        url = $form.attr("action");
        mydata = $form.serialize();
        var viewViz = $.ajax({
            type: 'POST',
            url: url,
            data: mydata,
            success: function(resultData) {
              if (resultData.success) {
                div_content = resultData.div_content
                divcol = '<div class="colexp" id="'+id+'"><a class="closediv" href="javascript:void(0)" onclick="removediv(\''+id+'\')">X</a>'+div_content+'</div>'
                $('#col-explore').prepend(divcol);
              }else{
                M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
              }
            },
            error:function(err) {
              M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
            },
        });
      }
    }
  });
  setTimeout(function(){
  	if($("#col").length>0){
  	  $( ".mdc-data-table__header-cell" ).click(function() {
  		 valth = $(this).html();
  		 var valueth = $("#col option").filter(function() {
  		  return $(this).text() === valth;
  		}).first().attr("value");
  		 $("#col").val(valueth).trigger("change");
  	  });
    }
  }, 2000);
});

//Remove data distribution div
function removediv(id){
  $("#"+id).remove();
}
//Hide or show data quality graph or table
function togglediv(){
  $("#dqlt").toggleClass("hide");
  $("#tqlt").toggleClass("hide");
}
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
    if ($("#issue_type").length > 0){
      $(".pfhide").addClass("hide");
      $("#issue_type").attr('required', false);
    }

    //$("#feedback_type").val("general");
    //$("#feedback_type_div").addClass("hide");
  }else{
    $("#replycomment").html("");
    $("#replyp").addClass("hide");
    $("#parent_feedback").val("");
    $("#comment").val("");
    if ($("#issue_type").length > 0){
      $(".pfhide").removeClass("hide");
      $("#issue_type").attr('required', true);
    }
    //$("#feedback_type_div").removeClass("hide");
    //$("#feedback_type").val("general");
  }
  $('html,body').animate({
  scrollTop: $("#feedback-form").offset().top-60},
  'slow');
}
$(document).ready(function() {
  $("#feedback_filter_type").on('change', function(e) {
    var val = $("#feedback_filter_type").val();
    if(val == ""){
      $(".feedli").removeClass("hide");
    }else{
      $(".feedli").addClass("hide");
      $("."+val).removeClass("hide");
    }
  });
});
