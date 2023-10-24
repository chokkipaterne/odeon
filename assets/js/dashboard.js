$(function(){
  $(window).scroll(function(){
    var aTop = $('.dash-menu').height();
    if($(this).scrollTop()>=aTop){
        $(".tp1").addClass("hide");
        $(".tp2").removeClass("hide");
    }else{
        $(".tp1").removeClass("hide");
        $(".tp2").addClass("hide");
    }
  });
});

$(document).ready(function(){
  setTimeout(function() {
      resizeViz();
      update_dash(false);
  }, 100);

  $('#modalConfirm').modal();

  var elem_filtout = document.querySelector('#filter-out');
  instance_filtout = M.Sidenav.init(elem_filtout, {
      edge:'right',
      draggable: false
  });

  $(".modal-yes").click(function() {
    var elem = document.querySelectorAll('#modalConfirm')[0];
    var instance = M.Modal.getInstance(elem);
    instance.close();
    $("#infodash-form").submit();
  });

  $('.datepicker').datepicker({"format":'yyyy-mm-dd',"autoClose":true});

  //Handle when user clicks on update dashboard
  $("#update-dash").click(function() {
      update_dash(true);
  });

  $(".modal-yes").click(function() {
    var elem = document.querySelectorAll('#modalConfirm')[0];
    var instance = M.Modal.getInstance(elem);
    instance.close();
    $("#infodash-form").submit();
  });

});

function update_dash(need_check){
  instance_filtout.close();
  var $form = $("#dash-form"),
  url = $form.attr("action");
  mydata = $form.serialize();
  //console.log(mydata);
  dash_file = $("#dash_file").val();
  nb_params = $("#nb_params").val();
  count = 0;
  var selected = [];
  $.each($("input[name='val-cat']:checked"), function(){
      selected.push($(this).val());
  });

  $(".dhviz").each(function() {
     let viz_code = $(this).data('id');
     let suffix = $(this).data('suffix');
     let file_code = $(this).data('file');
     if((file_code == dash_file && need_check) || !need_check){
       mydata_final = mydata + "&viz_code="+viz_code+"&suffix="+suffix+"&file="+file_code;
       target = viz_code+suffix;
       $("#"+target).addClass("loading");
       update_viz(url, mydata_final, viz_code, suffix, target);
     }
  });
}


function custom_dash(dash_code){
  $("#dash_code").val(dash_code);
  var elem = document.querySelectorAll('#modalConfirm')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}

function info_viz(viz_code){
  if($("#info"+viz_code).hasClass("hide")){
    $("#info"+viz_code).removeClass("hide");
  }else{
    $("#info"+viz_code).addClass("hide");
  }
}


function resizeViz(){
  window.dispatchEvent(new Event("resize"));
  /*$("#content-dash .dhviz").each(function() {
    var parent_width = $(this).width()-20;
    var elem = $(this).find('.plotly-graph-div');
    var width = elem.width();
    var id = elem.attr('id');
    if(width<parent_width){
      var update = {
          width: parent_width
      };
      var graph_div = document.getElementById(id);
      Plotly.relayout(graph_div, update)
    }
  });*/
}

function update_viz(url, mydata, viz_code, suffix, target){
    var updateViz = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(resultData) {
        $("#"+target).removeClass("loading");
        if (resultData.success) {
          $("#plot"+target).html(resultData.plot_div);
          resizeViz();
        }else{
          M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
        }
        //$('#viz-loader').hide();
      },
      error:function(err) {
        //$('#viz-loader').hide();
        $("#"+target).removeClass("loading");
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
    });
}

function copyToClipboard(str){
  const el = document.createElement('textarea');
  el.value = '<iframe src="'+str+'" width="500" height="1000" frameborder="0"></iframe>';
  el.setAttribute('readonly', '');
  el.style.position = 'absolute';
  el.style.left = '-9999px';
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
  M.toast({html: gettext("Successfully copy to clipboard"), classes: 'green rounded', displayLength:2000});
}
