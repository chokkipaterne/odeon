$(document).ready(function() {
    //$('.multi-options').select2();
    $("#obj_select").select2({
        placeholder: gettext("Select objective")
    });
    $('.tabs').tabs();
    $("#search_select").select2({
        placeholder: gettext("Select attributes")
    });
    if($("#user_type").val().trim() == 'expert'){
      if($("#code_viz_init").val().trim() != 'dash'){
        setTimeout(function() {
          $("#adv-opt").trigger("click");
        }, 100);
      }
    }else{
      if($("#code_viz_init").val().trim() != 'dash'){
        setTimeout(function() {
          $("#notadv-opt").trigger("click");
        }, 100);
      }
    }
    if($("#code_viz_init").val().trim() == 'dash'){
      if($("#dash-filt .dash-filt").length == 0 && parseInt($("#nbfiles").val()) == 1){
        /*setTimeout(function() {
            initFiltDash();
        }, 100);*/
      }
    }
});

$(document).ready(function(){
  setTimeout(function() {
      resizeViz();
  }, 100);

  $('#graph_color').ColorPicker({
  	onSubmit: function(hsb, hex, rgb, el) {
  		$(el).val(hex);
  		$(el).ColorPickerHide();
  	},
  	onBeforeShow: function () {
  		$(this).ColorPickerSetColor(this.value);
  	},
  	onChange: function (hsb, hex, rgb) {
  		$("#graph_color").val(hex);
  	}
  })
  .bind('keyup', function(){
  	$(this).ColorPickerSetColor(this.value);
  });

  //Init sidenav for list of viz types on right side
  var elem_viztype = document.querySelector('#list-viztypes');
  instance_viztype = M.Sidenav.init(elem_viztype, {
      edge:'right',
      draggable: false,
      onOpenStart: function() {
        init_viztypes();
      },
      onCloseStart: function() {
        init_vizmarks();
      }
  });

  var elem_trace = document.querySelector('#list-traces');
  var instance_trace = M.Sidenav.init(elem_trace, {
      edge:'right',
      draggable: false
  });

  /*var elem_alternviztypes = document.querySelector('#alternviztypes');
  instance_alternviztypes = M.Sidenav.init(elem_alternviztypes, {
      edge:'right',
      draggable: false,
      onOpenStart: function() {
        is_alter_viz = 1;
      },
      onCloseStart: function() {
        is_alter_viz = 0;
      }
  });*/

  //Search dimension or measures based on the input of search
  $("#search_dim").keyup(function() {
     var searchText = $(this).val().toLowerCase().trim();
     $(".mycol").each(function() {
        var string = $(this).data('name').toLowerCase().trim();
        if(string.indexOf(searchText)!=-1) {
          $(this).show();
        } else {
          $(this).hide();
        }
     });
  });

  $("#adv-opt").click(function() {
    $(".notadv").addClass("hide");
    $(".adv").removeClass("hide");
    $('.tabs').tabs('select','mymarks');
    //$("#adv-filt").removeClass("hide");
    //$("#adv-filt").removeClass("m4");
    //$("#adv-filt").addClass("m12");
    $('#obj_select').val(null).trigger('change');
  });

  $("#notadv-opt").click(function() {
    $(".notadv").removeClass("hide");
    $(".adv").addClass("hide");
    $('.tabs').tabs('select','adv-att');
    $("#step1").click();
    //$("#adv-filt").removeClass("m12");
    //$("#adv-filt").addClass("m4");
  });

  $("#step1").click(function() {
    //$("#adv-filt").addClass("hide");
    //$("#adv-obj").addClass("hide");
    //$("#adv-att").removeClass("hide");
  });

  $("#step2").click(function() {
    //$("#adv-filt").removeClass("hide");
    //$("#adv-obj").addClass("hide");
    //$("#adv-att").addClass("hide");
  });
  $("#finish1").click(function() {
    $("#viz-recommend").click();
  });
  $("#finish2").click(function() {
    $("#viz-recommend").click();
  });

  $("#step2a").click(function() {
    //$("#adv-filt").removeClass("hide");
    //$("#adv-obj").addClass("hide");
    //$("#adv-att").addClass("hide");
  });

  $("#step3").click(function() {
    //$("#adv-filt").addClass("hide");
    //$("#adv-obj").removeClass("hide");
    //$("#adv-att").addClass("hide");
  });

  //Search dimension or measures based on the input of search
  $("#search_graph").keyup(function() {
     search_word_graph();
  });
  $("#exact_search").change(function() {
     search_word_graph();
  });

  //Init modal for zoom viz and score settings
  $('#modalZoom').modal();
  $('#modalScoreSettings').modal();
  $('#modalConfirm').modal();

  $(".modal-yes").click(function() {
    var elem = document.querySelectorAll('#modalConfirm')[0];
    var instance = M.Modal.getInstance(elem);
    instance.close();
    $("#vizdrop-form").submit();
  });

  //Search Viz type when user is typing
  $("#search_viztype").keyup(function() {
     var searchText = $(this).val().toLowerCase().trim();
     $(".viztype").each(function() {
        var string = $(this).text().toLowerCase().trim();
        if(string.indexOf(searchText)!=-1) {
          $(this).show();
        } else {
          $(this).hide();
        }
     });
  });

  //Set multiple viz type
  $(".viztype").click(function() {
      let type_viz = $(this).data('id');
      if ($(this).hasClass("viztype-active")){
        $(this).removeClass("viztype-active");
        const index = list_type_viz_active.indexOf(type_viz);
        if (index > -1) {
          list_type_viz_active.splice(index, 1);
        }
        $(".viztype").removeClass("viztype-active");
      }else{
        $(".viztype").removeClass("viztype-active");
        list_type_viz_active = [];
        $(this).addClass("viztype-active");
        list_type_viz_active.push(type_viz);
        instance_viztype.close();
        if(change_viz_code != ""){
          let textvizu = $("#textvizu").html().toLowerCase().trim();
          if(textvizu.includes("create")){
            handle_change_viz();
          }
        }
      }
  });

  //Set only one viz type
  /*$(".viztype").click(function() {
      let type_viz = $(this).data('id');
      $("#type_viz").val(type_viz);
      $(".viztype").removeClass("viztype-active");
      $(this).addClass("viztype-active");
      instance_viztype.close();
  });*/

  //Modal for custom option of attribute
  $('#modalFeature').modal({
      dismissible: false,
      onCloseStart: function() {
        buffer_id = $("#modal-related").val();
        if(buffer_id){
          let optionfilt = $("#"+buffer_id).data('optionfilt');
          let valuefilt = $("#"+buffer_id).data('valuefilt');
          if(valuefilt){
            valuefilt = valuefilt.trim();
            valuefilt = valuefilt.replace(/#/g, "");
          }

          let target = $("#"+buffer_id).data('target');
          if(target == "data-filt" || target == "dash-filt"){
            if(optionfilt && (target == "data-filt" && valuefilt && valuefilt != "")){
              $("#"+buffer_id).show();
            }else if(optionfilt && (target == "dash-filt")){
              $("#"+buffer_id).show();
            }else{
              var drop_id = $("#"+buffer_id).data('target');
              $("#"+buffer_id).remove();
              if(drop_id){
                var count = $("#"+drop_id).children().length;
                if(count == 3){
                  $("#"+drop_id+'drop').show();
                  $("#"+drop_id+'help').remove();
                }
              }
            }
          }
        }
        buffer_id = "";
      }
    }
  );

  //Show/hide element based on selected option
  $('select[name="option-filt"]').on("change", function () {
      optionChange();
  });

  //Handle change option of attributes or filter
  $('input[type=radio][name=dim-meas-opt]').change(function() {
      if(date_option == 1){
          optionChange();
      }
  });
  $("#back-viz").click(function() {
    $("#back-viz").addClass("hide");
    /*var content_back = $("#content-back").html();
    $("#content-back").html("");
    $("#content-viz").html(content_back);*/
    var e = document.getElementById("content-viz");
    e.id = "content-back1";
    e = document.getElementById("content-back");
    e.id = "content-viz";
    e = document.getElementById("content-back1");
    e.id = "content-back";
    $('.tooltipped').tooltip();
    $('.material-tooltip').css('opacity', '0');
    if($("#content-viz .plot-div").length > 0){
      $("#graph-search").show();
    }
  });
  //Handle click on data operator for filter
  $(".data-operator").click(function() {
      let data_operator = $(this).data('id');
      $("#data_operator").val(data_operator);
      $(".data-operator").removeClass("active-viz");
      $(this).addClass("active-viz");
      //$("#viz-update").click();
  });
  $(".datakeep-operator").click(function() {
      let datakeep_operator = $(this).data('id');
      $("#datakeep_operator").val(datakeep_operator);
      $(".datakeep-operator").removeClass("active-viz");
      $(this).addClass("active-viz");
      //$("#viz-update").click();
  });

  //Function to handle which options are selected by the user
  $(".modal-apply").click(function() {
      var id = $("#modal-related").val();
      var elem = $("#"+id);
      let target = elem.data('target');
      let realtype = elem.data('realtype');
      let dimmeasopt = elem.data('dimmeasopt');
      let name = elem.data('name');
      let graphlabel = $("#graph_label").val();
      let graphcolor = $("#graph_color").val();
      let graphorder = $("#graph_order").val();

      if(target == "data-filt" || target == "dash-filt"){
        elem.data('dimmeasopt', "");
        elem.data('optionfilt', "");
        elem.data('valuefilt', "");
        elem.data('labelfilt', "");
        elem.data('fulltext', "");
        var full_text = "";
        let dimmeasopt = $("input[name='dim-meas-opt']:checked").attr('id');
        elem.data('dimmeasopt', dimmeasopt);
        if(dimmeasopt=="valexact"){
          full_text +=name;
        }else{
          full_text +=name+'('+gettext(dimmeasopt)+')';
        }
        var optionfilt = $('select[name="option-filt"] option:selected').val();
        elem.data('optionfilt', optionfilt);
        full_text +=' '+gettext(optionfilt);

        var valuefilt = "";
        var class_selected = $('select[name="option-filt"] option:selected').attr('class');
        if(class_selected.includes("need-value1")){
          valuefilt += $("#value-filt1").val();
          if(target == "dash-filt"){
            full_text +=' param';
          }else{
            full_text +=' '+$("#value-filt1").val();
          }
        }else if(class_selected.includes("need-value2")){
          valuefilt += $("#value-filt1").val();
          valuefilt += "##"+$("#value-filt2").val();
          if(target == "dash-filt"){
            full_text +=' param1'+gettext(' and ')+'param2';
          }else{
            full_text +=' '+$("#value-filt1").val()+gettext(' and ')+$("#value-filt2").val();
          }
        }else if(class_selected.includes("need-in")){
          var selected = [];
          $.each($("input[name='val-cat']:checked"), function(){
              selected.push($(this).val());
          });
          valuefilt = selected.join("##");
          if(selected.length == 1){
            full_text +=' '+selected[0];
          }else if(selected.length == 2){
            full_text +=' '+selected[0]+gettext(' and ')+selected[1];
          }else{
            full_text +=' '+gettext('chosen values');
          }
        }
        if(target == "dash-filt"){
          var labelfilt = $("#dash_label").val() || name;
          elem.data('labelfilt', labelfilt);
        }

        elem.data('valuefilt', valuefilt);
        elem.html(full_text);
        elem.data('fulltext', full_text);

        var elem = document.querySelectorAll('#modalFeature')[0];
        var instance = M.Modal.getInstance(elem);
        instance.close();
      }else{
        elem.data('dimmeasopt', "");
        elem.data('bins', "");
        let dimmeasopt = $("input[name='dim-meas-opt']:checked").attr('id');
        var bins = '';
        var full_text = "";
        if(dimmeasopt=="valexact"){
          full_text +=name;
        }else if(dimmeasopt=='bins'){
            bins = $("#val-bins").val() || '5';
            full_text +=name+'('+gettext(dimmeasopt)+":"+bins+')';
        }else{
          if(dimmeasopt && dimmeasopt != ""){
            full_text +=name+'('+gettext(dimmeasopt)+')';
          }else{
            full_text +=name
          }
        }
        elem.data('dimmeasopt', dimmeasopt);
        elem.data('bins', bins);
        elem.data('graphlabel', graphlabel);
        elem.data('graphcolor', graphcolor);
        elem.data('graphorder', graphorder);

        elem.html(full_text);
        elem.data('fulltext', full_text);

        var elem = document.querySelectorAll('#modalFeature')[0];
        var instance = M.Modal.getInstance(elem);
        instance.close();
      }
      //$("#viz-update").click();
  });

  //Function to handle submission of visualization attributes
  $("#viz-form").on("submit", function(event) {
    $("#res-title").html(gettext("Visualizations"));
    if ($("#vizresults").hasClass("hide")){
        $("#vizresults").removeClass("hide");
    }
    if(change_viz_code != ""){
      $("#chviz").val('1');
    }else{
      $("#chviz").val('0');
    }
      event.preventDefault();
      var submit_full_data = parseInt($("#submit_full_data").val());
      var visualization_action = $("#visualization_action").val();
      var visualization_code = $("#visualization_code").val();
      var files = [];
      var filters = [];
      var attribs = [];
      if(visualization_action == "empty_recommend_viz" || visualization_action == "dist_recommend_viz"){
          let file = $('.mycol').data('file');
          if(current_viz_file != ""){
            file = current_viz_file;
          }
          files.push(file);
          var can_pass = 1;
          $("#data-filt .data-filt").each(function() {
             let file = $(this).data('file');
             let filt = $(this).data();
             filters.push(filt);
             if(!files.includes(file)){
               files.push(file);
             }
             if(files.length > 1){
               can_pass = 0;
               files.pop();
               //M.toast({html: gettext("You can only choose dimensions & measures from same file"), classes: 'red rounded', displayLength:10000});
               //return;
             }
          });
          if(can_pass == 0){
            $("#data-filt .data-filt").each(function() {
               $(this).remove();
            });
            $("#data-filt"+'drop').show();
            if ($("#data-filt"+'help').length) {
              $("#data-filt"+'help').remove();
            }
            filters = [];
          }

          $("#files_viz").val(JSON.stringify(files));
          $("#data_filters_viz").val(JSON.stringify(filters));
      }else if(submit_full_data == 1){
          $(".vzmark").each(function() {
             let datamarks = [];
             let id = $(this).data('id');
             let mark = "vm"+id
             $("#"+mark+" ."+mark).each(function() {
                let file = $(this).data('file');
                let column = $(this).data();
                datamarks.push(column);
                if(!files.includes(file)){
                  files.push(file);
                }
                if(files.length > 1){
                  M.toast({html: gettext("You can only choose dimensions & measures from same file"), classes: 'red rounded', displayLength:10000});
                  return;
                }
             });
             $("#vzm"+id).val(JSON.stringify(datamarks));
          });
          if(visualization_action == "recommend_viz"){
            $("#vatt .vatt").each(function() {
               let file = $(this).data('file');
               let attrib = $(this).data();
               attribs.push(attrib);
               if(!files.includes(file)){
                 files.push(file);
               }
               if(files.length > 1){
                 M.toast({html: gettext("You can only choose dimensions & measures from same file"), classes: 'red rounded', displayLength:10000});
                 return;
               }
            });
            if(attribs.length < 1){
              M.toast({html: gettext("You must select at least one attribute"), classes: 'red rounded', displayLength:10000});
              return;
            }
          }
          $("#attribs_viz").val(JSON.stringify(attribs));
          $("#data-filt .data-filt").each(function() {
             let file = $(this).data('file');
             let filt = $(this).data();
             filters.push(filt);
             if(!files.includes(file)){
               files.push(file);
             }
             if(files.length > 1){
               M.toast({html: gettext("You can only choose dimensions & measures from same file"), classes: 'red rounded', displayLength:10000});
               return;
             }
          });

          $("#files_viz").val(JSON.stringify(files));
          $("#data_filters_viz").val(JSON.stringify(filters));
      }

      if($("#content-viz .loader").length > 0){
        $(".se-pre-con").fadeIn("slow");
        $(".spinner-loading").fadeIn("slow");
        $("#loader").fadeIn("slow");
      }else{
        $(".se-pre-con").fadeOut("slow");
        $(".spinner-loading").fadeOut("slow");
        $("#loader").fadeOut("slow");
      }
      var elem = document.querySelectorAll('#vizmarks-att')[0];
      var instance = M.Collapsible.getInstance(elem);
      instance.close(0);
      /*elem = document.querySelectorAll('#vizmarks-filt')[0];
      instance = M.Collapsible.getInstance(elem);
      instance.close(0);*/

      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      //$('#viz-loader').show();
      //console.log(mydata);
      var createViz = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if(!visualization_action.includes("recommend_viz")){
            if(change_viz_code != ""){
              //Erase graph code
              /*div_all = resultData.div_all
              div_all = div_all.replace('class="all_viz_details col s12 m12" id="'+change_viz_code+'"', "");
              div_all = div_all.replace('class="all_viz_details col s12 m6" id="'+change_viz_code+'"', "");
              $('#'+change_viz_code).html(div_all);
              $('.tooltipped').tooltip();
              $('.material-tooltip').css('opacity', '0');
              $('html,body').animate({
                    scrollTop: $("#"+change_viz_code).offset().top-40},
                    'slow');
              change_viz_code = "";
              resizeViz(1);*/
              //Save as new
              if($("#vizmarks-att").hasClass("hide")){
              }else{
                $("#vizmarks-att").addClass("hide");
              }
              $("#vizedit").addClass("hide");
              div_all = resultData.div_all;
              div_all = div_all.replace('m12', 'm6');
              if($("#"+change_viz_code).hasClass("m12")){
                $("#"+change_viz_code).removeClass("m12");
                $("#"+change_viz_code).addClass("m6");
              }
              $("#"+change_viz_code).parent().prepend($("#"+change_viz_code));
              $('#content-viz').prepend(div_all);
              $("#nbviz_tot").parent().prepend($("#nbviz_tot"));
              $('.tooltipped').tooltip();
              $('.material-tooltip').css('opacity', '0');
              try {
                $('html,body').animate({
                      scrollTop: $("#nbviz_tot").offset().top-60},
                      'slow');
              }catch(err) {
                $('#content-viz').prepend("<p id='nbviz_tot'><i><b>" + gettext("Help us provide you better visualization by rating these visualizations.") + "</b></i></p>");
              }
              change_viz_code = "";
              $('.rate-viz').click();
              resizeViz(1);
            }else{
              if(submit_full_data == 1){
                $('#content-viz').html(resultData.div_all);
              }else{
                $('#content-viz').append(resultData.div_all);
              }
              $('.tooltipped').tooltip();
              $('.material-tooltip').css('opacity', '0');
              $('.rate-viz').click();
              resizeViz(1);
              submit_other_viz();
            }
          }else{
            if(parseInt(resultData.nb_recommend_graph) == 0){
              if(visualization_action == "recommend_viz"){
                $('#alter-content-viz').html("<p>"+gettext("Unable to find some visualization recommendations")+"</p>");
              }else{
                $("#graph-search").hide();
                $('#content-viz').html("<p>"+gettext("Unable to find some visualization recommendations")+"</p>");
              }
            }
          }
          if($("#content-viz .loader").length > 0){
            $(".se-pre-con").fadeIn("slow");
            $(".spinner-loading").fadeIn("slow");
            $("#loader").fadeIn("slow");
          }else{
            $(".se-pre-con").fadeOut("slow");
            $(".spinner-loading").fadeOut("slow");
            $("#loader").fadeOut("slow");
          }
          //$('#viz-loader').hide();
        },
        error:function(err) {
          if(!visualization_action.includes("recommend_viz")){
            if(change_viz_code != ""){
              change_viz_code = "";
              M.toast({html: gettext("Unable to display the plot"), classes: 'red rounded', displayLength:10000});
            }
            submit_other_viz();
            if(submit_full_data == 1){
              $('#content-viz').html("<p>"+gettext("Unable to display the plot")+"</p>");
            }else{
              $('#content-viz').append("<p>"+gettext("Unable to display the plot")+"</p>");
            }
          }else{
            $('#content-viz').html("<p>"+gettext("Unable to find some visualization recommendataions")+"</p>");
          }
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});

          if($("#content-viz .loader").length > 0){
            $(".se-pre-con").fadeIn("slow");
            $(".spinner-loading").fadeIn("slow");
            $("#loader").fadeIn("slow");
          }else{
            $(".se-pre-con").fadeOut("slow");
            $(".spinner-loading").fadeOut("slow");
            $("#loader").fadeOut("slow");
          }
        },
      });
  });

  //List action traceability
  $(".history-viz").click(function() {
    $("#state").val("-1");
    var $form = $("#trace-form"),
    url = $form.attr("action");
    mydata = $form.serialize();
    var viewViz = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            results = resultData.results
            //console.log(results);

            $('#traces').html("");
            for(let i = 0; i < results.length; i++){
              let current_act = results[i];
              let date = current_act.date;
              let state = current_act.state;
              let insight = current_act.insight;
              let element ="<div class='action-trace col s12'>"
              //element +='<a draggable="true" onclick="loadState('+state+')" href="javascript:void(0)" class="tooltipped" data-state="'+state+'" data-position="top" data-tooltip="'+gettext("Load Data")+'" >';
              element +='<a draggable="true" onclick="loadState('+state+')" href="javascript:void(0)" class="trace" data-state="'+state+'" data-position="top" data-tooltip="'+gettext("Load Data")+'" >';
              element += "<b>"+date+"</b><br/>"+insight+'</a>'
              element +="</div>"
              $('#traces').append(element);
              $('.tooltipped').tooltip();
              $('.material-tooltip').css('opacity', '0');
            }
            instance_trace.open();
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
        },
        error:function(err) {
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
    });
  });

  //Search Viz type when user is typing
  $("#search_trace").keyup(function() {
     var searchText = $(this).val().toLowerCase().trim();
     $(".action-trace a").each(function() {
        var string = $(this).text().toLowerCase().trim();
        if(string.indexOf(searchText)!=-1) {
          $(this).parent(".action-trace").show();
        } else {
          $(this).parent(".action-trace").hide();
        }
     });
  });

  //Handle when user clicks on generate visualization
  $("#viz-update").click(function() {
    is_alter_viz = 0;
    if ($("#back-viz").hasClass("hide")){
    }else{
      $("#back-viz").addClass("hide");
    }
    let textvizu = $("#textvizu").html().toLowerCase().trim();
    if(textvizu.includes("create")){
      handle_viz_update();
    }else{
      handle_change_viz();
    }
  });

  //Handle change of select option
  $('select[name="set-opt"]').on("change", function () {
    var id = $(this).data('id');
    optionSetChange(id);
  });

  //handle when the user click on apply from score settings modal
  $(".modal-setapply").click(function() {
      var id = $("#viz-code").val();
      var elem = $("#scs"+id);
      var score_settings = "";

      $('.myfeat').each(function(index,item){
          let featid = $(item).data('id');
          let optval = $('#setopt'+featid+' option:selected').val();
          score_settings += featid+"_"+optval
          let class_selected = $('#setopt'+featid+' option:selected').attr('class');
          if(class_selected.includes("need-value1")){
            score_settings += "_"+$("#set1"+featid).val();
          }else if(class_selected.includes("need-value2")){
            score_settings += "_"+$("#set1"+featid).val();
            score_settings += "#"+$("#set2"+featid).val();
          }
          score_settings +="**";
      });
      score_settings = score_settings.substring(0, score_settings.length-2);
      elem.val(score_settings);

      var elem = document.querySelectorAll('#modalScoreSettings')[0];
      var instance = M.Modal.getInstance(elem);
      instance.close();
  });

  //handle action when the user clicks on save score
  $("#save-score").click(function() {
    var viz_codes = [];
    var viz_scores = [];
    var viz_types = [];
    var viz_type_marks = [];
    var viz_score_settings = [];
    $('.top_viz').each(function(index,item){
      let viz_code = $(item).data('id');
      let score = $("#sc"+viz_code).val();
      if(score != ""){
        viz_codes.push(viz_code);
        viz_scores.push(score);
        let viz_type = $("#vt"+viz_code).val();
        let viz_type_mark = $("#vtm"+viz_code).val();
        let viz_score_setting = $("#scs"+viz_code).val();
        viz_types.push(viz_type);
        viz_type_marks.push(viz_type_mark);
        viz_score_settings.push(viz_score_setting);
      }
    });
    if(viz_codes.length > 0){
      $("#viz_codes").val(JSON.stringify(viz_codes));
      $("#viz_scores").val(JSON.stringify(viz_scores));
      $("#viz_types").val(JSON.stringify(viz_types));
      $("#viz_type_marks").val(JSON.stringify(viz_type_marks));
      $("#viz_score_settings").val(JSON.stringify(viz_score_settings));
      $("#score-form").submit();
    }else{
      M.toast({html: gettext("Please assign score for at least one visualization"), classes: 'red rounded', displayLength:10000});
    }
  });

  //Function to handle submission of visualization attributes
  $("#score-form").on("submit", function(event) {
      event.preventDefault();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      //$('#viz-loader').show();
      //console.log(mydata);
      var registerScore = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            M.toast({html: gettext("Save score successfully"), classes: 'green rounded', displayLength:2000});
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
          //$('#viz-loader').hide();
        },
        error:function(err) {
          //$('#viz-loader').hide();
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
      });
  });

  //handle action when the user clicks on reorder score
  $("#reorder-score").click(function() {
    order_score();
  });

  //handle action when the user clicks on reorder score
  $("#empty-score").click(function() {
    $(".score").val("");
  });

  //Function to handle when adding visualization to dash
  $("#adddash-form").on("submit", function(event) {
      event.preventDefault();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      //$('#viz-loader').show();
      var adddash = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            //$("#content-dash").append(resultData.plot_div);
            //$('.tooltipped').tooltip();
            M.toast({html: gettext("Add to dashboard successfully"), classes: 'green rounded', displayLength:2000});
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
          //$('#viz-loader').hide();
        },
        error:function(err) {
          //$('#viz-loader').hide();
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
      });
  });

  //Function to handle when adding visualization to embed
  $("#embed-form").on("submit", function(event) {
      event.preventDefault();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      //$('#viz-loader').show();
      var embed = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            iframe = resultData.iframe;
            copyToClipboard(iframe);
            //$("#content-dash").append(resultData.plot_div);
            //$('.tooltipped').tooltip();
            M.toast({html: gettext("Successfully copy to clipboard"), classes: 'green rounded', displayLength:2000});
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
          //$('#viz-loader').hide();
        },
        error:function(err) {
          //$('#viz-loader').hide();
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
      });
  });


  $("#vizdrop-form").on("submit", function(event) {
      event.preventDefault();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      //$('#viz-loader').show();
      var viewViz = $.ajax({
          type: 'POST',
          url: url,
          data: mydata,
          success: function(resultData) {
            if (resultData.success) {
              $("#"+resultData.div_id).remove();
              M.toast({html: gettext("Deletion successful"), classes: 'green rounded', displayLength:2000});
            }else{
              M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
            }
            //$('#viz-loader').hide();
          },
          error:function(err) {
            //$('#viz-loader').hide();
            M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
          },
    });
  });

  /*$(".view-dash").click(function() {
      $(".for-dash").removeClass("hide");
      $(".for-viz").addClass("hide");
      setTimeout(function() {
          window.dispatchEvent(new Event("resize"));
      }, 100);
  });*/

  $(".list-viz").click(function() {
      $(".for-dash").addClass("hide");
      $(".for-viz").removeClass("hide");
  });

  //Handle when user clicks on save settings dashboard
  $("#dash-update").click(function() {
    $("#dashb-form").submit();
  });
  $("#dash-update1").click(function() {
    $("#dashb-form").submit();
  });


  //Function to handle submission of dashboard attributes
  $("#dashb-form").on("submit", function(event) {
      event.preventDefault();

      var files = [];
      var filters = [];
      var notes = [];

      $("#dash-filt .dash-filt").each(function() {
         let file = $(this).data('file');
         let filt = $(this).data();
         filters.push(filt);
         if(!files.includes(file)){
           files.push(file);
         }
         if(files.length > 1){
           M.toast({html: gettext("You can only choose dimensions & measures from same file"), classes: 'red rounded', displayLength:10000});
           return;
         }
      });

      $("#files_dash").val(JSON.stringify(files));
      $("#dash_filters").val(JSON.stringify(filters));

      $(".dhviz").each(function() {
         let id = $(this).data('id');
         let suffix = $(this).data('suffix');
         let note = {"code": id, "notes": $("#viznotes"+id+suffix).val(), "viz_final_title": $("#viztit"+id+suffix).val()
         , "show_nov": $("#shnov"+id+suffix).prop('checked'), "show_less": $("#shless"+id+suffix).prop('checked'), "show_adv": $("#shadv"+id+suffix).prop('checked')
       , "width": $("#vizwi"+id+suffix).val(), "height": $("#vizht"+id+suffix).val()};
         notes.push(note);
      });

      $("#allviz_notes").val(JSON.stringify(notes));

      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      //$('#viz-loader').show();
      //console.log(mydata);
      var createViz = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            M.toast({html: gettext("Save dashboard settings successfully"), classes: 'green rounded', displayLength:2000});
            $("#dash-view")[0].click();
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
          //$('#viz-loader').hide();
        },
        error:function(err) {
          //$('#viz-loader').hide();
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
      });
  });

  //Handle when user clicks on create new viz
  $(".add-viz").click(function() {
    $("#graph-search").hide();
    emptyViz();
    if($("#user_type").val().trim()=='non-expert' || $("#user_type").val().trim()=='intermediate'){
    	$("#notadv-opt").trigger("click");
    }else{
    	$("#adv-opt").trigger("click");
    }
  });

  //Handle when user clicks on recommend visualization
  $("#viz-recommend").click(function() {
    is_alter_viz = 0;
    if ($("#back-viz").hasClass("hide")){
    }else{
      $("#back-viz").addClass("hide");
    }
    handle_recommend_viz();
  });

  setTimeout(function() {
  	/*var first_file = $("#distviz0").data('keyfile').trim();
  	dist_recommend_viz(first_file);*/
    //$("#distviz0").click();
    var code_viz_init = $("#code_viz_init").val().trim();
    if(code_viz_init == 'get-recommendations'){
      $("#recomdviz0").click();
    }
    if(code_viz_init == 'get-distribution'){
      $("#distviz0").click();
    }
    if(code_viz_init == 'get-tasks'){
      if($(".tasksmviz").length > 0){
        $(".tasksmviz")[0].click();
      }
    }
  }, 300);

  $("#attr_select").on('change', function(e) {
     var data = $(this).select2('data');
     emptyViz(3);
     for(let i = 0; i < data.length; i++){
       let current_data = data[i];
       let value = current_data.id;
	     value = value.replace(/'/g, '"');
       let elem = JSON.parse(value);
       let drop_id = "vatt";
       var elemDrop = $("#"+drop_id);

       var generate_id = generate();
        let id = generate_id;
        let myclass = "chosen "+drop_id;
        let ty = elem['ty'];
        let dt = elem['dt'];
        let type = elem['type'];
        let realtype = elem['realtype'];
        let name = elem['name'];
        let file = elem['file'];
        let target = "vatt";
        var count = $("#"+drop_id).children().length;
        let labelfilt = elem['labelfilt'] || '';
        let valuefilt = elem['valuefilt'] || '';
        let dimmeasopt = elem['dimmeasopt'];
        let fulltext = elem['fulltext'];
        let bins = elem['bins'] || '';
        let graphlabel = elem['graphlabel'] || "";
        let graphcolor = elem['graphcolor'] || "";
        let graphorder = elem['graphorder'] || "";

        var elemt = '<a data-target="'+drop_id+'" id="'+drop_id+id+count+'" href="javascript:void(0)"';
        elemt += ' onclick="customizeField(event)" draggable="true" ondragstart="removeElem(event)" class="'+myclass+'" data-ty="'+ty+'" ';
        elemt += ' data-type="'+type+'" data-name="'+name+'" ';
        elemt += ' data-realtype="'+realtype+'" ';
        elemt += ' data-dt="'+dt+'" ';
        elemt += ' data-labelfilt="'+labelfilt+'" ';
        elemt += ' data-graphlabel="'+graphlabel+'" ';
        elemt += ' data-graphcolor="'+graphcolor+'" ';
        elemt += ' data-graphorder="'+graphorder+'" ';
        elemt += ' data-valuefilt="'+valuefilt+'" ';
        elemt += ' data-dimmeasopt="'+dimmeasopt+'" ';
        elemt += ' data-fulltext="'+fulltext+'" ';
        elemt += ' data-bins="'+bins+'" ';
        elemt += ' data-file="'+file+'">'+fulltext+'</a>';
        elemDrop.append(elemt);
     }
     let drop_id = "vatt";
     if(data.length>0){
       $("#"+drop_id+'drop').hide();
       var help = '<p id="'+drop_id+'help" class="center sm-marg"><i>'+gettext("Drag to remove element or click on the element to setup some options")+'</i></p>';
       $("#"+drop_id).append(help);
     }
  });
  $("#obj_select").on('change', function(e) {
     var data = $(this).select2('data');
     var obj_data = "0";
     for(let i = 0; i < data.length; i++){
       let current_data = data[i];
       let value = current_data.id;
	     obj_data = obj_data + ","+ value;
     }
     $("#obj_data").val(obj_data)
  });
  $("#search_select").on('change', function(e) {
     var data = $(this).select2('data');
     var obj_data = "";
     for(let i = 0; i < data.length; i++){
       let current_data = data[i];
       let value = current_data.id;
	     obj_data = obj_data + " "+ value;
     }
     $("#search_graph").val(obj_data);
     search_word_graph();
  });

  $('#shdsp_typ').change(function () {
  	var shdsp_typ = $('#shdsp_typ').is(":checked");
  	if(shdsp_typ){
  		$(".svdt").removeClass("hide");
  	}else{
  		$(".svdt").addClass("hide");
  	}
  });

});
