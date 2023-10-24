$(document).ready(function(){
  setTimeout(function() {
      resizeViz();
      update_embed(false);
  }, 100);
});

function update_embed(need_check){
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
       mydata_final = mydata + "&viz_code="+viz_code+"&suffix="+suffix+"&file="+file_code+"&embed=1";
       target = viz_code+suffix;
       $("#"+target).addClass("loading");
       update_viz(url, mydata_final, viz_code, suffix, target);
     }
  });
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
