var buffer_id = "";
var date_option = 0;
var list_type_viz_active = [];
var can_run_next_viz_type = false;
var is_dash = false;
var timerId = "";
var nb_recommend_graph = 0;
var end_recommend_graph = 0;
var list_viz_show = [];
var empty_type_viz = 0;
var current_viz_file = "";
var target_y = "vm2";
var target_z = "vm5";
var target_x = "vm1";
var target_shape = "vm4";
var target_color = "vm3";
var target_animation = "vm11";
var target_dimensions = "vm10";
var target_facet_col = "vm9";
var target_facet_row = "vm8";
var target_label = "vm6";
var target_att = "vatt";
var pass_move = 0;
var change_viz_code = "";
var load_more = 1;
var current_vzcode_recommend_graph = "";
var tot_nb_vizs_recommend = 0;
var tot_nb_vizs_deducted = 0;
var instance_viztype = "";
var instance_alternviztypes = "";
var is_alter_viz = 0;
var back_end_recommend_graph = 0;
var back_nb_recommend_graph =  0;
var back_tot_nb_vizs_recommend = 0;
var back_tot_nb_vizs_deducted = 0;
var back_vzcode_recommend_graph = "";
var back_load_more = 0;

//Handle drop function
function allowDrop(ev) {
  ev.preventDefault();
}

//Handle drag function
function drag(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
}

//Remove element from element
function removeElem(ev){
  ev.preventDefault();
  var removeElem = $("#"+ev.target.id);
  var drop_id = removeElem.data('target');
  removeElem.remove();
  if(drop_id){
    var count = $("#"+drop_id).children().length;
    if(count == 3){
      $("#"+drop_id+'drop').show();
      $("#"+drop_id+'help').remove();
    }
  }
}
function removeElemId(targetid){
  var removeElem = $("#"+targetid);
  var drop_id = removeElem.data('target');
  removeElem.remove();
  if(drop_id){
    var count = $("#"+drop_id).children().length;
    if(count == 3){
      $("#"+drop_id+'drop').show();
      $("#"+drop_id+'help').remove();
    }
  }
}

//Handle drop function
function drop(ev) {
  ev.preventDefault();
  var drag_id = ev.dataTransfer.getData("text");
  var drop_id = ev.target.id;
  var elemType = ev.target.nodeName;

  if(drop_id && elemType == "DIV"){
    move(drag_id, drop_id);
  }else{
    drop_id = ev.target.closest("div").id;
    move(drag_id, drop_id);
  }
}

String.prototype.shuffle = function () {
  var a = this.split(""),
      n = a.length;
  for(var i = n - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i];
      a[i] = a[j];
      a[j] = tmp;
  }
  return a.join("");
}

//Generate unique id for element
function generate() {
  return '_' + Math.random().toString(36).substr(2, 9);
}

//Generate unique id for viz
function generate_viz_code() {
  code = Math.random().toString(36).substr(2, 9);
  code = code.shuffle();
  return code;
}

//Move element from one div to another div
function move(drag_id, drop_id){
  pass_move = 1;
  if(drop_id == 'data-filt'){
    var elem = document.querySelectorAll('#vizmarks-att')[0];
    var instance = M.Collapsible.getInstance(elem);
    instance.open(0);
  }
  if(drop_id == 'vatt'){
    var elem = document.querySelectorAll('#vizmarks-att')[0];
    var instance = M.Collapsible.getInstance(elem);
    instance.open(0);
    $("#notadv-opt").trigger("click");
  }

  var elemDrag = $("#"+drag_id);
  var elemDrop = $("#"+drop_id);

  if(buffer_id){
    $("#"+buffer_id).remove();
    buffer_id = "";
  }

  var elemDropTarget = elemDrop.data('target');
  if(elemDropTarget){
    elemDrop = $("#"+elemDropTarget);
    drop_id = elemDropTarget;
  }

  let id = drag_id;
  var generate_id = generate();
  id = id +""+generate_id;
  let myclass = "chosen "+drop_id;
  let ty = elemDrag.data('ty');
  let dt = elemDrag.data('dt');
  let type = elemDrag.data('type');
  let realtype = elemDrag.data('realtype');
  let name = elemDrag.data('name');
  let file = elemDrag.data('file');
  var count = $("#"+drop_id).children().length;

  if((drop_id=="data-filt" || drop_id=="dash-filt") && (realtype == "lon" || realtype == "lat" || realtype == "shape" || realtype == "point")){
    M.toast({html: gettext("You can't use this attribute as filter"), classes: 'orange rounded', displayLength:8000});
    return;
  }

  /*Give feedback for users based on datatype and viz mark*/
  if(realtype == "str" && drop_id != target_label){
    M.toast({html: gettext("This datatype isn't suitable for this visualization mark"), classes: 'orange rounded', displayLength:8000});
  }
  if(drop_id == target_x){
    if(realtype == "str" || realtype == "lon"){
      M.toast({html: gettext("This visualization mark is best suitable to nominal, temporal, numerical, latitude, geo point and geo shape data"), classes: 'orange rounded', displayLength:8000});
    }
  }
  if(drop_id == target_y){
    if(realtype != "int" && realtype != "float" && realtype != "lon" && realtype != "auto"){
      M.toast({html: gettext("This visualization mark is best suitable to numerical and longitude data"), classes: 'orange rounded', displayLength:8000});
    }
  }
  if(drop_id == target_color || drop_id == target_shape){
    if(realtype != "cat" && realtype != "bool"){
      M.toast({html: gettext("This visualization mark is best suitable to nominal data"), classes: 'orange rounded', displayLength:8000});
    }
  }
  if(drop_id == target_z){
    if(realtype != "int" && realtype != "float" && realtype != "auto"){
      M.toast({html: gettext("This visualization mark is best suitable to numerical data"), classes: 'orange rounded', displayLength:8000});
    }
  }
  if(drop_id == target_facet_col || drop_id == target_facet_row || drop_id == target_animation){
    if(realtype != "cat" && realtype != "bool" && realtype != "date"){
      M.toast({html: gettext("This visualization mark is best suitable to nominal and temporal data"), classes: 'orange rounded', displayLength:8000});
    }
  }

  if(count == 2){
    $("#"+drop_id+'drop').hide();
  }
  if(drop_id != "data-filt" && drop_id != "dash-filt"){
    if(realtype == "int" || realtype == "float" || realtype == "date"){
      myclass = myclass + " down"
    }else{
      myclass = myclass + " down"
    }
  }else{
    myclass = myclass + " down"
  }

  var elem = '<a data-target="'+drop_id+'" id="'+drop_id+id+count+'" href="javascript:void(0)"';
  elem += ' onclick="customizeField(event)" draggable="true" ondragstart="removeElem(event)" class="'+myclass+'" data-ty="'+ty+'" ';
  elem += ' data-type="'+type+'" data-name="'+name+'" ';
  elem += ' data-realtype="'+realtype+'" ';
  elem += ' data-dt="'+dt+'" ';
  elem += ' data-file="'+file+'">'+name+'</a>';
  if($("#"+drop_id+"help")){
    $("#"+drop_id+"help").remove();
  }
  var help = '<p id="'+drop_id+'help" class="center sm-marg"><i>'+gettext("Drag to remove element or click on the element to setup some options")+'</i></p>';
  buffer_id = drop_id+id+count;

  if(drop_id=="data-filt" || drop_id=="dash-filt"){
    elemDrop.append(elem);
    $("#"+buffer_id).hide();
    $("#"+buffer_id).data('optionfilt', '');
    $("#"+buffer_id).data('valuefilt', '');
    $("#"+buffer_id).data('dimmeasopt', 'valexact');
    $("#"+buffer_id).data('fulltext', name);
    if(realtype == "bool"){
      $("#"+buffer_id).data('optionfilt', 'istrue');
    }else if(realtype == "date"){
      $("#"+buffer_id).data('dimmeasopt', 'ymd');
      $("#"+buffer_id).data('optionfilt', 'isbetween');
    }else if(realtype == "float" || realtype == "int"){
      $("#"+buffer_id).data('optionfilt', 'isbetween');
    }else if(realtype == "cat"){
      $("#"+buffer_id).data('optionfilt', 'in');
    }
    $("#"+buffer_id).trigger("click");
  }else{
    count = $("#"+drop_id).children().length;
    maxelements = elemDrop.data('maxelements') + 1;
    elemDrop.append(elem);
    $("#"+buffer_id).data('fulltext', name);
    if(count > maxelements){
      $("#"+buffer_id).remove();
      M.toast({html: gettext("You can only assign maximum")+" "+(maxelements-1)+" "+gettext("attribute to this visualisation mark"), classes: 'red rounded', displayLength:10000});
    }else{
      if(($("#user_type").val().trim()=='non-expert' || $("#user_type").val().trim()=='intermediate') && (realtype == "int" || realtype == "float")){
        $("#"+buffer_id).data('dimmeasopt', 'avg');
        $("#"+buffer_id).data('fulltext', name+'(avg)');
        $("#"+buffer_id).text(name+'(avg)');
      }else if(($("#user_type").val().trim()=='non-expert' || $("#user_type").val().trim()=='intermediate') && (realtype == "date")){
        $("#"+buffer_id).data('dimmeasopt', 'ymd');
        $("#"+buffer_id).data('fulltext', name+'(ymd)');
        $("#"+buffer_id).text(name+'(ymd)');
      }else{
        $("#"+buffer_id).data('dimmeasopt', 'valexact');
      }
    }
    buffer_id = "";
  }
  elemDrop.append(help);
}

//Function to set more options for selected attributes
function customizeField(ev){
  var id = ev.target.id;
  var elem = $("#"+id);
  let target = elem.data('target');
  let realtype = elem.data('realtype');
  let dimmeasopt = elem.data('dimmeasopt');
  let name = elem.data('name');
  let file_name = elem.data('file');
  let bins = elem.data('bins') || '10';
  let viz_type = elem.data('viztype') || 'auto';
  let graphlabel = elem.data('graphlabel') || "";
  let graphcolor = elem.data('graphcolor') || "";
  let graphorder = elem.data('graphorder') || "";
  $("#dim-meas-options").show();


  //Destroy datetime elements
  var date1 = document.querySelectorAll('#value-filt1')[0];
  var instance1 = M.Datepicker.getInstance(date1);
  if(instance1){
    instance1.destroy();
  }
  var date2 = document.querySelectorAll('#value-filt2')[0];
  var instance2 = M.Datepicker.getInstance(date2);
  if(instance2){
    instance2.destroy();
  }

  $("#value-filt1").attr("placeholder", gettext("Value"));
  $("#value-filt2").attr("placeholder", gettext("Value"));
  date_option = 0

  if(target == "data-filt" || target == "dash-filt"){
    $(".for-graph").hide();
    $("#graph_label").val("");
    $("#graph_color").val("");
    $("#graph_order").val("");
    $("#value-filt1").val("");
    $("#value-filt2").val("");
    $("#filter-option").val("");
    $("#modal-related").val(id);
    $("#filter").show();
    $("#dim-meas-options").hide();

    $("#filter-value1").hide();
    $("#filter-value2").hide();
    $("#categories").hide();

    if(target == "dash-filt"){
      is_dash = true;
      $("#filter-label").show();
      let labelfilt = elem.data('labelfilt') || name;
      $("#dash_label").val(labelfilt);
    }else{
      $("#filter-label").hide();
    }

    let optionfilt = elem.data('optionfilt');
    let valuefilt = elem.data('valuefilt');

    if(!dimmeasopt){
      dimmeasopt = "valexact";
    }
    $('#'+dimmeasopt).prop('checked', true);

    if(realtype == 'float' || realtype == 'int' || realtype == 'auto'){
      if(realtype == 'auto' && target == "dash-filt"){
          M.toast({html: gettext("No setup available for that element"), classes: 'orange rounded', displayLength:8000});
          if(buffer_id){
            $("#"+buffer_id).remove();
            buffer_id = "";
          }
          return false;
      }
      if(realtype != 'auto' && target != "dash-filt"){
        $("#dim-meas-options").show();
      }
      $(".for-string").hide();
      $(".for-date").hide();
      $(".for-categorical").hide();
      $(".for-bool").hide();
      $(".for-numerical").show();
    }else if(realtype == 'str'){
      $(".for-date").hide();
      $(".for-categorical").hide();
      $(".for-bool").hide();
      $(".for-numerical").hide();
      $(".for-string").show();
    }else if(realtype == 'bool'){
      if(target == "data-filt"){
        $(".for-date").hide();
        $(".for-categorical").hide();
        $(".for-string").hide();
        $(".for-numerical").hide();
        $(".for-bool").show();
      }else{
        M.toast({html: gettext("No setup available for that element"), classes: 'orange rounded', displayLength:8000});
        if(buffer_id){
          $("#"+buffer_id).remove();
          buffer_id = "";
        }
        return false;
      }
    }else if(realtype == 'date'){
      date_option = 1;
      $('#'+dimmeasopt).prop('checked', true);
      $("#dim-meas-options").show();
      $(".for-categorical").hide();
      $(".for-string").hide();
      $(".for-numerical").hide();
      $(".for-bool").hide();
      $(".for-date").show();
    }else if(realtype == 'cat'){
      $("#un_column").val(name);
      $("#un_file").val(file_name);
      var $form = $("#unique-form"),
      url = $form.attr("action");
      mydata = $form.serialize();
      var viewViz = $.ajax({
          type: 'POST',
          url: url,
          data: mydata,
          success: function(resultData) {
            if (resultData.success) {
              //console.log(resultData.unique_values);
              unique_values = resultData.unique_values
              options = "";
              options += "<div class='col m4 s6 truncate'><label><input type='checkbox' id='cat-all'/><span>"+gettext("Select All")+"</span></label></div>";
              for (i = 0; i < unique_values.length; i++) {
                options += "<div class='col m4 s6 truncate'><label><input name='val-cat' value='"+unique_values[i]+"' class='cat-item' type='checkbox'/><span>"+unique_values[i]+"</span></label></div>";
              }
              $("#categories").html(options);
              $("#cat-all").click(function () {
                  $('.cat-item').prop('checked', this.checked);
              });
              if(valuefilt || pass_move == 1){
                var arr = valuefilt.split("##");
                var class_selected = $('select[name="option-filt"] option:selected').attr('class');
                if(class_selected.includes("need-in")){
                  $("#categories").show();
                  setTimeout(function(){
                    $.each(arr, function(i, val){
                      //console.log(val);
                       $("input[name='val-cat'][value='" + val + "']").prop('checked', true);
                    });
                  }, 100);
                }
              }
              if(pass_move == 1 && target == "dash-filt"){
                $('.cat-item').prop('checked', true);
                $(".title-feat").html(gettext("Setup Filter: ")+name);
                var elem = document.querySelectorAll('#modalFeature')[0];
                var instance = M.Modal.getInstance(elem);
                instance.open();
                $(".modal-apply").trigger("click");
                //instance.close();
              }
              pass_move = 0;
            }else{
              M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
              if(pass_move == 1 && target == "dash-filt"){
                $(".title-feat").html(gettext("Setup Filter: ")+name);
                var elem = document.querySelectorAll('#modalFeature')[0];
                var instance = M.Modal.getInstance(elem);
                instance.open();
                instance.close();
              }
              pass_move = 0;
            }
          },
          error:function(err) {
            M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
            if(pass_move == 1 && target == "dash-filt"){
              $(".title-feat").html(gettext("Setup Filter: ")+name);
              var elem = document.querySelectorAll('#modalFeature')[0];
              var instance = M.Modal.getInstance(elem);
              instance.open();
              instance.close();
            }
            pass_move = 0;

          },
      });

      $(".for-date").hide();
      $(".for-bool").hide();
      $(".for-numerical").hide();
      $(".for-string").show();
      $(".for-categorical").show();
    }
    $(".not-filt").hide();

    if(target == "dash-filt"){
      $(".not-dash").hide();
    }

    if(optionfilt){
      $("#filter-option option[value='"+optionfilt+"']").prop("selected", true);
    }else{
      $("#filter-option option[value='']").prop("selected", true);
    }
    if(valuefilt || pass_move == 1){
      var arr = valuefilt.split("##");
      var class_selected = $('select[name="option-filt"] option:selected').attr('class');
      if(class_selected.includes("need-value1") && target != "dash-filt"){
        $("#filter-value1").show();
        $("#value-filt1").val(arr[0]);
        if(realtype == 'date'){
          if(dimmeasopt == 'ymd'){
            $("#value-filt1").attr("placeholder", "yyyy-mm-dd");
            $('#value-filt1').datepicker({"format":'yyyy-mm-dd',
            "autoClose":true, "defaultDate": new Date(arr[0])});
          }else if(dimmeasopt == 'valexact'){
            $("#value-filt1").attr("placeholder", "yyyy-mm-dd hh:ii");
          }else if(dimmeasopt == 'y'){
            $("#value-filt1").attr("placeholder", "yyyy");
          }else if(dimmeasopt == 'ym'){
            $("#value-filt1").attr("placeholder", "yyyy-mm");
          }else if(dimmeasopt == 'hi'){
            $("#value-filt1").attr("placeholder", "hh:ii");
          }else{
            $("#value-filt1").attr("placeholder", gettext("Value"));
          }
        }
      }else if(class_selected.includes("need-value2") && target != "dash-filt"){
        $("#filter-value1").show();
        $("#filter-value2").show();
        $("#value-filt1").val(arr[0]);
        $("#value-filt2").val(arr[1]);
        if(realtype == 'date'){
          if(dimmeasopt == 'valexact'){
            $("#value-filt1").attr("placeholder", "yyyy-mm-dd hh:ii");
            $("#value-filt2").attr("placeholder", "yyyy-mm-dd hh:ii");
          }else if(dimmeasopt == 'y'){
            $("#value-filt1").attr("placeholder", "yyyy");
            $("#value-filt2").attr("placeholder", "yyyy");
          }else if(dimmeasopt == 'ym'){
            $("#value-filt1").attr("placeholder", "yyyy-mm");
            $("#value-filt2").attr("placeholder", "yyyy-mm");
          }else if(dimmeasopt == 'ymd'){
            $("#value-filt1").attr("placeholder", "yyyy-mm-dd");
            $("#value-filt2").attr("placeholder", "yyyy-mm-dd");
            $('#value-filt1').datepicker({"format":'yyyy-mm-dd', "autoClose":true, "defaultDate": new Date(arr[0])});
            $('#value-filt2').datepicker({"format":'yyyy-mm-dd', "autoClose":true, "defaultDate": new Date(arr[1])});
          }else if(dimmeasopt == 'hi'){
            $("#value-filt1").attr("placeholder", "hh:ii");
            $("#value-filt2").attr("placeholder", "hh:ii");
          }else{
            $("#value-filt1").attr("placeholder", gettext("Value"));
            $("#value-filt2").attr("placeholder", gettext("Value"));
          }
        }
      }
    }

    if(($("#user_type").val().trim()=='non-expert' || $("#user_type").val().trim()=='intermediate')){
      $("#dim-meas-options").hide();
    }
    if(pass_move == 1){
      if(realtype != 'cat'){
        pass_move = 0;
      }
      if(target == "dash-filt"){
        if(realtype != 'cat'){
          $(".title-feat").html(gettext("Setup Filter: ")+name);
          var elem = document.querySelectorAll('#modalFeature')[0];
          var instance = M.Modal.getInstance(elem);
          instance.open();
          $(".modal-apply").trigger("click");
        }
      }else{
        $(".title-feat").html(gettext("Setup Filter: ")+name);
        var elem = document.querySelectorAll('#modalFeature')[0];
        var instance = M.Modal.getInstance(elem);
        instance.open();
      }
    }else{
      $(".title-feat").html(gettext("Setup Filter: ")+name);
      var elem = document.querySelectorAll('#modalFeature')[0];
      var instance = M.Modal.getInstance(elem);
      instance.open();
    }
  }else{
    $(".for-graph").show();
    $("#graph-label").show();
    $("#graph-color").show();
    $("#graph-order").show();

    $("#graph_label").val(graphlabel);
    $("#graph_color").val(graphcolor);
    $("#graph_order").val(graphorder);
    if(target == target_z){
      $("#graph-order").hide();
    }
    if(target == target_y || target == target_x || target == target_z || target == target_att){
    }else{
      $("#graph-color").hide();
    }
    if(realtype == 'float' || realtype == 'int' || realtype == 'str' || realtype == 'cat'){
    }else{
      $("#graph-order").hide();
    }
    $("#modal-related").val(id);
    $("#filter").hide();
    $(".for-numerical").hide();
    $(".for-date").hide();
    $("#dim-meas-options").show();
    $("#pdim").hide();
    $('.with-gap').prop('checked', false);
    if(realtype == 'float' || realtype == 'int' || realtype == 'date'){
      $("#pdim").show();
      if(dimmeasopt){
        $('#'+dimmeasopt).prop('checked', true);
      }
      $("#val-bins").val(bins);
      if(realtype == 'float' || realtype == 'int'){
        $(".for-date").hide();
        $(".for-numerical").show();
        if(target == "vatt"){
        }else if(target == target_y || target == target_z){
          $(".for-not-yz").hide();
        }else if(target == target_x){
          $(".for-yz").hide();
        }else{
          $(".for-yz").hide();
        }
      }else{
        $(".for-numerical").hide();
        $(".for-date").show();
      }
    }
    $(".title-feat").html(gettext("Setup Attribute: ")+name);
    var elem = document.querySelectorAll('#modalFeature')[0];
    var instance = M.Modal.getInstance(elem);
    instance.open();
    /*else{
      //M.toast({html: gettext("No setup available for that element"), classes: 'orange rounded', displayLength:8000});
    }*/
  }
}

//function to handle change of options in data filter
function optionChange(){
  var class_selected = $('select[name="option-filt"] option:selected').attr('class');
  let dimmeasopt = $("input[name='dim-meas-opt']:checked").attr('id');
  //Destroy datetime elements
  var date1 = document.querySelectorAll('#value-filt1')[0];
  var instance1 = M.Datepicker.getInstance(date1);
  if(instance1){
    instance1.destroy();
  }
  var date2 = document.querySelectorAll('#value-filt2')[0];
  var instance2 = M.Datepicker.getInstance(date2);
  if(instance2){
    instance2.destroy();
  }
  $("#value-filt1").attr("placeholder", gettext("Value"));
  $("#value-filt2").attr("placeholder", gettext("Value"));

  if(class_selected.includes("need-value1") && !is_dash){
    if(dimmeasopt == 'ymd'){
      $("#value-filt1").attr("placeholder", "yyyy-mm-dd");
      $('#value-filt1').datepicker({"format":'yyyy-mm-dd',
      "autoClose":true});
    }else if(dimmeasopt == 'valexact' && date_option == 1){
      $("#value-filt1").attr("placeholder", "yyyy-mm-dd hh:ii");
    }else if(dimmeasopt == 'y'){
      $("#value-filt1").attr("placeholder", "yyyy");
    }else if(dimmeasopt == 'ym'){
      $("#value-filt1").attr("placeholder", "yyyy-mm");
    }else if(dimmeasopt == 'hi'){
      $("#value-filt1").attr("placeholder", "hh:ii");
    }else{
      $("#value-filt1").attr("placeholder", gettext("Value"));
    }
    $("#filter-value1").show();
    $("#filter-value2").hide();
    $("#categories").hide();
  }
  else if(class_selected.includes("need-value2") && !is_dash){
    if(dimmeasopt == 'valexact' && date_option == 1){
      $("#value-filt1").attr("placeholder", "yyyy-mm-dd hh:ii");
      $("#value-filt2").attr("placeholder", "yyyy-mm-dd hh:ii");
    }else if(dimmeasopt == 'y'){
      $("#value-filt1").attr("placeholder", "yyyy");
      $("#value-filt2").attr("placeholder", "yyyy");
    }else if(dimmeasopt == 'ym'){
      $("#value-filt1").attr("placeholder", "yyyy-mm");
      $("#value-filt2").attr("placeholder", "yyyy-mm");
    }else if(dimmeasopt == 'ymd'){
      $("#value-filt1").attr("placeholder", "yyyy-mm-dd");
      $("#value-filt2").attr("placeholder", "yyyy-mm-dd");
      $('#value-filt1').datepicker({"format":'yyyy-mm-dd', "autoClose":true});
      $('#value-filt2').datepicker({"format":'yyyy-mm-dd', "autoClose":true});
    }else if(dimmeasopt == 'hi'){
      $("#value-filt1").attr("placeholder", "hh:ii");
      $("#value-filt2").attr("placeholder", "hh:ii");
    }else{
      $("#value-filt1").attr("placeholder", gettext("Value"));
      $("#value-filt2").attr("placeholder", gettext("Value"));
    }
    $("#filter-value1").show();
    $("#filter-value2").show();
    $("#categories").hide();
  }
  else if(class_selected.includes("need-in")){
    $("#filter-value1").hide();
    $("#filter-value2").hide();
    $("#categories").show();
  }
  else{
    $("#filter-value1").hide();
    $("#filter-value2").hide();
    $("#categories").hide();
  }
}

function submit_other_viz(){
  if(can_run_next_viz_type == false){
    can_run_next_viz_type = true;
    var i;
    for (i = 1; i < list_type_viz_active.length; i++) {
      $("#graph-search").show();
      $("#submit_full_data").val(0);
      $("#type_viz").val(list_type_viz_active[i]);
      $("#visualization_action").val("update_viz");
      $("#visualization_code").val(generate_viz_code());
      $("#viz-form").submit();
    }
  }
}

//Handle when user clicks on button zoom
function zoom(id){
    id = $.trim(id);
    var viz_content = $("#plot"+id).html();
    var graph_div = $("#plot"+id).find('.plotly-graph-div');
    var graph_div_id = graph_div.attr('id');
    //console.log(graph_div_id);
    var title = gettext("Zoom visulization");
    if($("#vzn"+id).val() != ""){
      title = $("#vzn"+id).val()
    }
    var dynre = new RegExp(graph_div_id, "g");
    viz_content = viz_content.replace(dynre, graph_div_id+'z');
    if(title.includes("map") || title.includes("scatter") || title.includes("bubble")){
      add_to_plot_div = 'document.getElementById("'+graph_div_id+'z'+'").innerHTML = "";'
      viz_content = viz_content.replace('<script type="text/javascript">', '<script type="text/javascript"> '+add_to_plot_div);
    }

    $("#zoom-title").html(title);
    $("#zoom-viz").html(viz_content);
    var elem = document.querySelectorAll('#modalZoom')[0];
    var instance = M.Modal.getInstance(elem);
    instance.open();
    setTimeout(function() {
        window.dispatchEvent(new Event("resize"));
    }, 100);
    /*setTimeout(function() {
      var graph_divz = document.getElementById(graph_div_id+'z');
      Plotly.relayout(graph_divz, update);
    }, 100);*/
}

function initViz(id){
  id = $.trim(id);
  var viz_content = "";
  var graph_div = ""
  if($("#plot"+id).length > 0){
    viz_content = $("#plot"+id).html();
    graph_div = $("#plot"+id).find('.plotly-graph-div');
  }else{
    viz_content = $("#plotd"+id).html();
    graph_div = $("#plotd"+id).find('.plotly-graph-div');
  }

  var graph_div_id = graph_div.attr('id');

  var title = "";
  if($("#vzn"+id).length > 0){
    if($("#vzn"+id).val() != ""){
      title += $("#vzn"+id).val()
    }
  }else{
    if($("#vznd"+id).val() != ""){
      title += $("#vznd"+id).val()
    }
  }
  var dynre = new RegExp(graph_div_id, "g");
  viz_content = viz_content.replace(dynre, graph_div_id+'e');
  if(title.includes("map") || title.includes("scatter") || title.includes("bubble")){
    add_to_plot_div = 'document.getElementById("'+graph_div_id+'e'+'").innerHTML = "";'
    viz_content = viz_content.replace('<script type="text/javascript">', '<script type="text/javascript"> '+add_to_plot_div);
  }
  $("#vizedit").html(viz_content);
  $("#vizedit").prepend("<p class='sm-marg center'>"+gettext("<b>Initial Viz</b><br/>")+"<small>"+title+"</small></p>");
  setTimeout(function() {
      window.dispatchEvent(new Event("resize"));
  }, 100);
}

//Handle when user clicks on button hide/show settings
function hide_vizdetails(id){
  id = $.trim(id);
  if ($("#divsc"+id).hasClass("hide")){
    $("#divsc"+id).removeClass("hide");
    $("#divvzn"+id).removeClass("hide");
    $("#divsc"+id).addClass("show");
    $("#divvzn"+id).addClass("show");
  }else{
    $("#divsc"+id).removeClass("show");
    $("#divvzn"+id).removeClass("show");
    $("#divsc"+id).addClass("hide");
    $("#divvzn"+id).addClass("hide");
  }
}

//Handle when user clicks on button score settings
function score_settings(id){
  $(".for-bool").show();
  $(".for-numerical").show();
  id = $.trim(id);
  $("#viz-code").val(id);
  scs = $("#scs"+id).val();
  var arr = scs.split("**");
  for (i = 0; i < arr.length; i++) {
    feat = arr[i];
    split = feat.split("_");
    featid = split[0];
    optid = split[1];
    if(optid.length > 0 && optid != ""){
      $("#setopt"+featid).val(optid);
    }else{
      $("#setopt"+featid).val("");
    }
    optionSetChange(featid);
    if (split.length == 3) {
      val = split[2];
      values = val.split("#");
      $("#set1"+featid).val("");
      $("#set2"+featid).val("");
      if(values.length > 0){
        $("#set1"+featid).val(values[0]);
      }
      if(values.length > 1){
        $("#set2"+featid).val(values[1]);
      }
    }
  }
  var elem = document.querySelectorAll('#modalScoreSettings')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}

//function to handle change of options in score settings
function optionSetChange(id){
  var class_selected = $('#setopt'+id+' option:selected').attr('class');
  if(class_selected && typeof class_selected !== 'undefined' && class_selected !== null){
    if(class_selected.includes("need-value1")){
      $("#setv1"+id).show();
      $("#setv2"+id).hide();
    }else if(class_selected.includes("need-value2")){
      $("#setv1"+id).show();
      $("#setv2"+id).show();
    }
  }else{
    $("#setv1"+id).hide();
    $("#setv2"+id).hide();
  }
}

//Handle when user clicks on button add to dashboard
function add_to_dash(id){
  $("#add_code").val(id);
  $("#add_viz_notes").val($("#vzn"+id).val());
  $("#add_type_viz").val($("#vt"+id).val());
  $("#add_viz_data").val($("#vd"+id).val());
  $("#add_plot_div").val($("#plot"+id).html());
  $("#adddash-form").submit();
}

function add_to_embed(id){
  $("#embed_code").val(id);
  $("#embed_viz_notes").val($("#vzn"+id).val());
  $("#embed_type_viz").val($("#vt"+id).val());
  $("#embed_viz_data").val($("#vd"+id).val());
  $("#embed_plot_div").val($("#plot"+id).html());
  $("#embed-form").submit();
}

//Copy to clipboard
function copyToClipboard(str){
  const el = document.createElement('textarea');
  el.value = str;
  el.setAttribute('readonly', '');
  el.style.position = 'absolute';
  el.style.left = '-9999px';
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
}

//Handle when user clicks on button add to dashboard
function rm_from_dash(id){
  $("#drop_code").val(id);
  var elem = document.querySelectorAll('#modalConfirm')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}

function emptyViz(resetall=1){
  //Empty list of selected visualisation type
  list_type_viz_active = [];
  list_viz_show = [];
  $("#viz_grouping").val("");
  $("#viz_orientation").val("");
  $(".viztype").each(function() {
    if ($(this).hasClass("viztype-active")){
      $(this).removeClass("viztype-active");
    }
  });
  if(resetall == 3){
    $("#vatt .vatt").each(function() {
       $(this).remove();
    });
    $("#vatt"+'drop').show();
    if ($("#vatt"+'help').length) {
      $("#vatt"+'help').remove();
    }
  }else{
    //Empty list of visualisation marks
    $(".vzmark").each(function() {
       let id = $(this).data('id');
       let mark = "vm"+id
       $("#"+mark+" ."+mark).each(function() {
          $(this).remove();
       });
       $("#"+mark+'drop').show();
       if ($("#"+mark+'help').length) {
         $("#"+mark+'help').remove();
       }
    });
  }
  if(resetall == 1){
    $("#vatt .vatt").each(function() {
       $(this).remove();
    });
    $("#vatt"+'drop').show();
    if ($("#vatt"+'help').length) {
      $("#vatt"+'help').remove();
    }

    $("#data-filt .data-filt").each(function() {
       $(this).remove();
    });
    $("#data-filt"+'drop').show();
    if ($("#data-filt"+'help').length) {
      $("#data-filt"+'help').remove();
    }
  }
  if(resetall < 2){
    if(is_alter_viz == 1){
      $('#alter-content-viz').html("");
    }else{
      $('#content-viz').html("");
    }
  }
}

function get_nb_recommend(vzcode_recommend_graph){
  //$("#loader").fadeIn("slow");
  var max_viz_shown = $("#max_viz_shown").val();
  var nbrecommend = $.ajax({
    type: 'GET',
    url: '/nb-recommend/'+vzcode_recommend_graph+"/",
    success: function(resultData) {
      if (resultData.success) {
        new_nb_recommend_graph = parseInt(resultData.nb_recommend_graph);
        new_end_recommend_graph = parseInt(resultData.end_recommend_graph);
        tot_nb_vizs_recommend = parseInt(resultData.nb_recommend_graph);
        if(load_more > 1 && is_alter_viz != 1){
          new_end_recommend_graph = back_end_recommend_graph;
      	  new_nb_recommend_graph = back_tot_nb_vizs_recommend;
      	  tot_nb_vizs_recommend = back_tot_nb_vizs_recommend;
        }
        var max_vizs = 0;
        if(load_more != 0){
          max_vizs = load_more * max_viz_shown
          if(new_nb_recommend_graph > max_vizs){
            new_nb_recommend_graph = max_vizs;
          }
        }
        if(new_nb_recommend_graph > 0 && new_nb_recommend_graph != nb_recommend_graph){
          var i;
          for (i = nb_recommend_graph; i < new_nb_recommend_graph; i++) {
            get_recommend_graph(vzcode_recommend_graph, i);
          }
        }
        end_recommend_graph = new_end_recommend_graph;
        nb_recommend_graph =  new_nb_recommend_graph;
        var ldmore = "load-more";
        if(is_alter_viz == 1){
          ldmore = "alter-load-more";
        }else{
          if(load_more >= 1){
            back_end_recommend_graph = end_recommend_graph;
          	back_nb_recommend_graph =  nb_recommend_graph;
          	back_tot_nb_vizs_recommend = tot_nb_vizs_recommend;
          	back_tot_nb_vizs_deducted = tot_nb_vizs_deducted;
          	back_vzcode_recommend_graph = vzcode_recommend_graph;
            back_load_more = load_more;
          }
        }
        if(end_recommend_graph == 0){
          get_nb_recommend(vzcode_recommend_graph);
        }
        if(end_recommend_graph == 1){
          if(nb_recommend_graph != tot_nb_vizs_recommend){
            if ($("#"+ldmore).hasClass("hide")){
              $("#"+ldmore).removeClass("hide");
            }
          }else{
            if ($("#"+ldmore).hasClass("hide")){
            }else{
              $("#"+ldmore).addClass("hide");
            }
          }
        }else{
          if ($("#"+ldmore).hasClass("hide")){
          }else{
            $("#"+ldmore).addClass("hide");
          }
        }
      }
    }
  });
}

function get_recommend_graph(vzcode_recommend_graph, i){
  var visualization_code = vzcode_recommend_graph + (i+1);
  var class_div = "s12 m6"
  if(is_alter_viz == 1){
    class_div = "s12 m12"
  }
  /*if (i == 0){
    class_div = "s12"
  }*/
  if(is_alter_viz != 1){
    if(i > 0){
      $("#graph-search").show();
    }else{
      $("#graph-search").hide();
    }
  }
  let loader = $("#viz-loader").html();
  var div_all = '<div class="all_viz_details col loader '+class_div+'" id="'+visualization_code+'">'+loader+'</div>';
  if(is_alter_viz == 1){
    $('#alter-content-viz').append(div_all);
  }else{
    $('#content-viz').append(div_all);
  }
  var nbrecommend = $.ajax({
    type: 'GET',
    url: '/get-recommend/'+visualization_code+"/",
    success: function(resultData) {
      $("#"+visualization_code).removeClass("loader");
      if (resultData.success) {
        var top_div = "";
        /*if(i == 0){
          top_div = "<b>"+gettext("best recommendation")+"</b><br/>";
        }*/
        $("#"+visualization_code).html(top_div+resultData.div_all);
        $('.tooltipped').tooltip();
        $('.material-tooltip').css('opacity', '0');
      }else{
        tot_nb_vizs_deducted = tot_nb_vizs_deducted + 1;
        $("#"+visualization_code).remove();
      }
      if(is_alter_viz == 0){
        order_score(1);
      }else{
        $('.rate-viz').click();
        var nbviztot = tot_nb_vizs_recommend - tot_nb_vizs_deducted;
        if ($("#alter-load-more").hasClass("hide")){
          nbviztot = $('#alter-content-viz .all_viz_details').length;
        }
        $("#nbalt").html("("+nbviztot+")");
        $("#alter-content-viz .ahtml").addClass("hide");
        $("#alter-content-viz .a2html").addClass("hide");
      }
    },
    error:function(err) {
      $("#"+visualization_code).removeClass("loader");
      $("#"+visualization_code).remove();
      //$("#"+visualization_code).html("<p>"+gettext("Unable to display the plot")+"</p>");
    },
  });
}

function resizeViz(viz=0){
  window.dispatchEvent(new Event("resize"));
  /*if(viz == 0){
    $("#content-dash .dhviz").each(function() {
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
    });
  }else{
    $("#content-viz .all_viz_details").each(function() {
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
    });
  }*/
}

function init_viztypes(){
  var list_marks = [];
  list_viz_show = [];
  $(".vzmark").each(function() {
   let id = $(this).data('id');
   let mark = "vm"+id
   var count = $("#"+mark+" ."+mark).length;
   if(count > 0){
     list_marks.push(''+id);
   }
  });
  var viz_orientation = $("#viz_orientation").val();
  if(viz_orientation.length > 0){
    list_marks.push(''+$("#viz_orientation").data('id'));
  }
  var viz_grouping = $("#viz_grouping").val();
  if(viz_grouping.length > 0){
    list_marks.push(''+$("#viz_grouping").data('id'));
  }
  //console.log(list_marks);
  $(".viztype").each(function() {
    var marks = $(this).data('marks');
    let type_viz = $(this).data('id');
    marks = marks.replace(" ", "");
    var viztype_marks = marks.split(",");
    let intersection = list_marks.filter(x => viztype_marks.includes(x));
    //console.log(viztype_marks);
    //console.log(intersection);
    if(intersection.length == list_marks.length){
      $(this).removeClass("ctshow");
      $(this).addClass("cnshow");
      list_viz_show.push(type_viz);
    }else{
      $(this).removeClass("cnshow");
      $(this).addClass("ctshow");
    }
  });
}

function init_vizmarks(){
  list_type_viz_active  = [];
  list_viz_show = [];
  var list_marks = [];
  $(".vzmark").each(function() {
   let id = $(this).data('id');
   list_marks.push(''+id);
  });
  list_marks.push(''+$("#viz_orientation").data('id'));
  list_marks.push(''+$("#viz_grouping").data('id'));
  $(".viztype").each(function() {
    let type_viz = $(this).data('id');
    if($(this).hasClass("cnshow")){
      list_viz_show.push(type_viz);
    }
    if ($(this).hasClass("viztype-active") && $(this).hasClass("cnshow")){
      var marks = $(this).data('marks');
      marks = marks.replace(" ", "");
      var viztype_marks = marks.split(",");
      list_type_viz_active.push(type_viz);
      let intersection = list_marks.filter(x => viztype_marks.includes(x));
      list_marks = intersection.slice();
    }
  });

  $(".vzmark").each(function() {
   let id = ""+$(this).data('id');
   let mark = "vm"+id;
   if(list_marks.includes(id)){
     $("#"+mark).removeClass("ctshow");
     $("#"+mark).addClass("cnshow");
     $("#div"+mark).removeClass("ctshow");
     $("#div"+mark).addClass("cnshow");
   }else{
     $("#"+mark+" ."+mark).each(function() {
        $(this).remove();
     });
     $("#"+mark).removeClass("cnshow");
     $("#"+mark).addClass("ctshow");
     $("#div"+mark).removeClass("cnshow");
     $("#div"+mark).addClass("ctshow");
   }
  });
  let id = ""+$("#viz_orientation").data('id');
  if(list_marks.includes(id)){
    $(".vms"+id).removeClass("ctshow");
    $(".vms"+id).addClass("cnshow");
    $("#divvm"+id).removeClass("ctshow");
    $("#divvm"+id).addClass("cnshow");
  }else{
    $("#viz_orientation").val("");
    $(".vms"+id).removeClass("cnshow");
    $(".vms"+id).addClass("ctshow");
    $("#divvm"+id).removeClass("cnshow");
    $("#divvm"+id).addClass("ctshow");
  }
  id = ""+$("#viz_grouping").data('id');
  if(list_marks.includes(id)){
    $(".vms"+id).removeClass("ctshow");
    $(".vms"+id).addClass("cnshow");
    $("#divvm"+id).removeClass("ctshow");
    $("#divvm"+id).addClass("cnshow");
  }else{
    $("#viz_grouping").val("");
    $(".vms"+id).removeClass("cnshow");
    $(".vms"+id).addClass("ctshow");
    $("#divvm"+id).removeClass("cnshow");
    $("#divvm"+id).addClass("ctshow");
  }
}

function alterViz(viz_code){
  if($("#vizmarks-att").hasClass("hide")){
  }else{
    $("#vizmarks-att").addClass("hide");
  }
  $('#content-viz .all_viz_details').removeClass("boxactive");
  $("#nbalt").html("(0)");
  $("#"+viz_code).addClass("boxactive");
  $("#alter_data").val($("#vd"+viz_code).val());
  $("#vizedit").addClass("hide");
  is_alter_viz = 1;
  $("#textvizu").text(gettext("Create Visualization"));
  var code_viz_init = $("#code_viz_init").val();
  $("#notadv-opt").trigger("click");
  var viz_data = $("#vd"+viz_code).val();
  var json_data = JSON.parse(viz_data);
  emptyViz(3);
  var data = json_data.result.final_graph_parameters;
  change_viz_code = "";

  $(".vzmark").each(function() {
     let id = $(this).data('id');
     let drop_id = "vatt";
     var elemDrop = $("#"+drop_id);
     let marks = data["vzm"+id];
     var i;
     for (i = 0; i < marks.length; i++) {
        var elem = marks[i];
        var generate_id = generate();
        let id = generate_id;
        let myclass = "chosen "+drop_id;
        let ty = elem['ty'];
        let dt = elem['dt'];
        let type = elem['type'];
        let realtype = elem['realtype'];
        let name = elem['name'];
        let file = elem['file'];
        let target = elem['target'];
        var count = $("#"+drop_id).children().length;
        let labelfilt = elem['labelfilt'] || '';
        let graphlabel = elem['graphlabel'] || "";
        let graphcolor = elem['graphcolor'] || "";
        let graphorder = elem['graphorder'] || "";
        let valuefilt = elem['valuefilt'] || '';
        let dimmeasopt = elem['dimmeasopt'];
        let fulltext = elem['fulltext'];
        let bins = elem['bins'] || '';

        if(drop_id != "data-filt" && drop_id != "dash-filt"){
          if(realtype == "int" || realtype == "float" || realtype == "date"){
            myclass = myclass + " down"
          }else{
            myclass = myclass + " down"
          }
        }else{
          myclass = myclass + " down"
        }

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
  });
  let drop_id = "vatt";
  $("#"+drop_id+'drop').hide();
  var help = '<p id="'+drop_id+'help" class="center sm-marg"><i>'+gettext("Drag to remove element or click on the element to setup some options")+'</i></p>';
  $("#"+drop_id).append(help);

  var elem = document.querySelectorAll('#vizmarks-att')[0];
  var instance = M.Collapsible.getInstance(elem);
  instance.open(0);
  //instance_alternviztypes.open();
  openAlt();
  /*if ($("#back-viz").hasClass("hide")){
    $("#back-viz").removeClass("hide");
  }*/
  //var content_viz = $("#content-viz").html();
  //$("#content-back").html(content_viz);
  /*var e = document.getElementById("content-viz");
  e.id = "content-back1";
  e = document.getElementById("content-back");
  e.id = "content-viz";
  e = document.getElementById("content-back1");
  e.id = "content-back";*/
  //$("#viz-update").click();
  handle_recommend_viz();
}

function loadFieldsDashViz(viz_code){
  $(".for-dash").addClass("hide");
  $(".for-viz").removeClass("hide");
  loadFieldsViz(viz_code);
}

function loadFieldsViz(viz_code){
  if($("#vizmarks-att").hasClass("hide")){
    $("#vizmarks-att").removeClass("hide");
  }
  if(!$("#vizedit").hasClass("hide")){
    $("#vizedit").addClass("hide");
  }
  //instance_alternviztypes.close();
  closeAlt();
  is_alter_viz = 0;
  $("#viz-update").text(gettext("Save as New"));
  $("#lab-update").html(gettext("Click on 'Save as New' when you are done with the above settings"))
  $("#textvizu").text(gettext("Edit Visualization"));
  if($("#notadv-opt").hasClass("hide")){
  }else{
    $("#notadv-opt").addClass("hide");
  }

  $("#adv-opt").trigger("click");
  var viz_data = $("#vd"+viz_code).val();
  var json_data = JSON.parse(viz_data);
  emptyViz(2);
  var data = json_data.result.final_graph_parameters;
  var type_viz = data.type_viz;
  var viz_grouping = data.viz_grouping;
  var viz_orientation = data.viz_orientation;
  $("#viz_grouping").val(viz_grouping);
  $("#viz_orientation").val(viz_orientation);
  $("#viztype"+type_viz).addClass("viztype-active");
  list_type_viz_active.push(type_viz);
  change_viz_code = viz_code;

  $(".vzmark").each(function() {
     let id = $(this).data('id');
     let drop_id = "vm"+id;
     var elemDrop = $("#"+drop_id);
     elemDrop.show();
     let marks = data["vzm"+id];
     var i;
     for (i = 0; i < marks.length; i++) {
        var elem = marks[i];
        var generate_id = generate();
        let id = generate_id;
        let myclass = "chosen "+drop_id;
        let ty = elem['ty'];
        let dt = elem['dt'];
        let type = elem['type'];
        let realtype = elem['realtype'];
        let name = elem['name'];
        let file = elem['file'];
        let target = elem['target'];
        var count = $("#"+drop_id).children().length;
        let labelfilt = elem['labelfilt'] || '';
        let graphlabel = elem['graphlabel'] || "";
        let graphcolor = elem['graphcolor'] || "";
        let graphorder = elem['graphorder'] || "";
        let valuefilt = elem['valuefilt'] || '';
        let dimmeasopt = elem['dimmeasopt'];
        let fulltext = elem['fulltext'];
        let bins = elem['bins'] || '';

        if(drop_id != "data-filt" && drop_id != "dash-filt"){
          if(realtype == "int" || realtype == "float" || realtype == "date"){
            myclass = myclass + " down"
          }else{
            myclass = myclass + " down"
          }
        }else{
          myclass = myclass + " down"
        }

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
     if(marks.length>0){
       $("#"+drop_id+'drop').hide();
       $("#div"+drop_id).show();
       var help = '<p id="'+drop_id+'help" class="center sm-marg"><i>'+gettext("Drag to remove element or click on the element to setup some options")+'</i></p>';
       elemDrop.append(help);
     }else{
       if(($("#user_type").val().trim()=='non-expert' || $("#user_type").val().trim()=='intermediate')){
         elemDrop.hide();
         $("#div"+drop_id).hide();
       }
     }
  });
  var elem = document.querySelectorAll('#vizmarks-att')[0];
  var instance = M.Collapsible.getInstance(elem);
  instance.open(0);
  $('html,body').animate({
        scrollTop: $("#mymarks").offset().top-115},
        'slow');
  if($("#allmarks").hasClass("m12")){
    $("#allmarks").removeClass("m12");
    $("#allmarks").addClass("m8");
  }else{
    $("#allmarks").addClass("m8");
  }
  if($("#vizedit").hasClass("hide")){
    $("#vizedit").removeClass("hide");
  }
  initViz(viz_code);
}

function changeFieldsViz(viz_code){
  $("#textvizu").text(gettext("Create Visualization"));
  $("#adv-opt").trigger("click");
  var viz_data = $("#vd"+viz_code).val();
  var json_data = JSON.parse(viz_data);
  emptyViz(2);
  var data = json_data.result.final_graph_parameters;
  var type_viz = data.type_viz;
  var viz_grouping = data.viz_grouping;
  var viz_orientation = data.viz_orientation;
  //$("#viz_grouping").val(viz_grouping);
  //$("#viz_orientation").val(viz_orientation);
  //$("#viztype"+type_viz).addClass("viztype-active");
  //list_type_viz_active.push(type_viz);
  change_viz_code = viz_code;

  $(".vzmark").each(function() {
     let id = $(this).data('id');
     let drop_id = "vm"+id;
     var elemDrop = $("#"+drop_id);
     elemDrop.show();
     let marks = data["vzm"+id];
     var i;
     for (i = 0; i < marks.length; i++) {
        var elem = marks[i];
        var generate_id = generate();
        let id = generate_id;
        let myclass = "chosen "+drop_id;
        let ty = elem['ty'];
        let dt = elem['dt'];
        let type = elem['type'];
        let realtype = elem['realtype'];
        let name = elem['name'];
        let file = elem['file'];
        let target = elem['target'];
        var count = $("#"+drop_id).children().length;
        let labelfilt = elem['labelfilt'] || '';
        let graphlabel = elem['graphlabel'] || "";
        let graphcolor = elem['graphcolor'] || "";
        let graphorder = elem['graphorder'] || "";
        let valuefilt = elem['valuefilt'] || '';
        let dimmeasopt = elem['dimmeasopt'];
        let fulltext = elem['fulltext'];
        let bins = elem['bins'] || '';

        if(drop_id != "data-filt" && drop_id != "dash-filt"){
          if(realtype == "int" || realtype == "float" || realtype == "date"){
            myclass = myclass + " down"
          }else{
            myclass = myclass + " down"
          }
        }else{
          myclass = myclass + " down"
        }

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
     if(marks.length>0){
       $("#"+drop_id+'drop').hide();
       $("#div"+drop_id).show();
       var help = '<p id="'+drop_id+'help" class="center sm-marg"><i>'+gettext("Drag to remove element or click on the element to setup some options")+'</i></p>';
       elemDrop.append(help);
     }else{
       elemDrop.hide();
       $("#div"+drop_id).hide();
     }
  });
  $("#choose-viztype").trigger("click");
}

function handle_recommend_viz(act="recommend_viz"){
  load_more = 1;
  $("#submit_full_data").val(1);
  action = act;
  $("#visualization_action").val(action);
  var expert = parseFloat($("#expert").val() || 0.0);
  var intermediate = parseFloat($("#intermediate").val() || 0.0);
  var nonexpert = parseFloat($("#non-expert").val() || 0.0);
  var total = expert + intermediate + nonexpert;
  var threshold = parseFloat($("#threshold").val() || 0.0);
  total = parseFloat(total);
  if(total != parseFloat("100")){
    M.toast({html: gettext("Sum of weights must be equal to 100"), classes: 'red rounded', displayLength:10000});
  }else if(threshold > parseFloat("10") || threshold < parseFloat("0")){
    M.toast({html: gettext("Threshold must be less or equal to 10"), classes: 'red rounded', displayLength:10000});
  }else{
    nb_recommend_graph = 0;
    end_recommend_graph = 0;
    var vzcode_recommend_graph = generate_viz_code();
    current_vzcode_recommend_graph = vzcode_recommend_graph;
    if(action == "recommend_viz"){
      emptyViz(0);
    }else{
      $('#content-viz').html("");
    }
    $("#visualization_code").val(vzcode_recommend_graph);
    $("#viz-form").submit();
    tot_nb_vizs_deducted = 0;
    get_nb_recommend(vzcode_recommend_graph);
  }
}

function empty_recommend_viz(viz_file="",is_task=0){
  closeAlt();
  if($("#vizmarks-att").hasClass("hide")){
  }else{
    $("#vizmarks-att").addClass("hide");
  }
  if(!$("#vizedit").hasClass("hide")){
    $("#vizedit").addClass("hide");
  }
  load_more = 1;
  action = "empty_recommend_viz"
  $("#submit_full_data").val(1);
  $("#is_task").val(is_task);
  $("#visualization_action").val(action);
  var expert = parseFloat($("#expert").val() || 0.0);
  var intermediate = parseFloat($("#intermediate").val() || 0.0);
  var nonexpert = parseFloat($("#non-expert").val() || 0.0);
  var total = expert + intermediate + nonexpert;
  var threshold = parseFloat($("#threshold").val() || 0.0);
  total = parseFloat(total);
  if(total != parseFloat("100")){
    M.toast({html: gettext("Sum of weights must be equal to 100"), classes: 'red rounded', displayLength:10000});
  }else if(threshold > parseFloat("10") || threshold < parseFloat("0")){
    M.toast({html: gettext("Threshold must be less or equal to 10"), classes: 'red rounded', displayLength:10000});
  }else{
    nb_recommend_graph = 0;
    end_recommend_graph = 0;
    var vzcode_recommend_graph = generate_viz_code();
    current_vzcode_recommend_graph = vzcode_recommend_graph;
    emptyViz(0);
    current_viz_file = viz_file;
    $("#visualization_code").val(vzcode_recommend_graph);
    $("#viz-form").submit();
    tot_nb_vizs_deducted = 0;
    get_nb_recommend(vzcode_recommend_graph);
  }
}

function dist_recommend_viz(viz_file=""){
  closeAlt();
  if($("#vizmarks-att").hasClass("hide")){
  }else{
    $("#vizmarks-att").addClass("hide");
  }
  if(!$("#vizedit").hasClass("hide")){
    $("#vizedit").addClass("hide");
  }
  load_more = 1;
  action = "dist_recommend_viz"
  $("#submit_full_data").val(1);
  $("#visualization_action").val(action);
  var expert = parseFloat($("#expert").val() || 0.0);
  var intermediate = parseFloat($("#intermediate").val() || 0.0);
  var nonexpert = parseFloat($("#non-expert").val() || 0.0);
  var total = expert + intermediate + nonexpert;
  var threshold = parseFloat($("#threshold").val() || 0.0);
  total = parseFloat(total);
  if(total != parseFloat("100")){
    M.toast({html: gettext("Sum of weights must be equal to 100"), classes: 'red rounded', displayLength:10000});
  }else if(threshold > parseFloat("10") || threshold < parseFloat("0")){
    M.toast({html: gettext("Threshold must be less or equal to 10"), classes: 'red rounded', displayLength:10000});
  }else{
    nb_recommend_graph = 0;
    end_recommend_graph = 0;
    var vzcode_recommend_graph = generate_viz_code();
    current_vzcode_recommend_graph = vzcode_recommend_graph;
    emptyViz(0);
    current_viz_file = viz_file;
    $("#visualization_code").val(vzcode_recommend_graph);
    $("#viz-form").submit();
    tot_nb_vizs_deducted = 0;
    get_nb_recommend(vzcode_recommend_graph);
  }
}

function load_more_graph(){
  closeAlt();
  is_alter_viz = 0;
  var vzcode_recommend_graph = current_vzcode_recommend_graph;

  end_recommend_graph = back_end_recommend_graph;
  nb_recommend_graph = back_nb_recommend_graph;
  tot_nb_vizs_recommend = back_tot_nb_vizs_recommend;
  tot_nb_vizs_deducted = back_tot_nb_vizs_deducted;
  vzcode_recommend_graph = back_vzcode_recommend_graph;
  load_more = back_load_more;

  load_more = load_more + 1;
  get_nb_recommend(vzcode_recommend_graph);
}

function alter_load_more_graph(){
  is_alter_viz = 1;
  var vzcode_recommend_graph = current_vzcode_recommend_graph;
  load_more = load_more + 1;
  get_nb_recommend(vzcode_recommend_graph);
}

function search_word_graph(){
  var exact_search = $('#exact_search').is(":checked");
  var searchText = $("#search_graph").val().toLowerCase().trim();
  var array_texts = searchText.split(" ");
  if(array_texts.length == 1){
    limit = 1
  }else{
    if(exact_search){
      limit = parseInt(array_texts.length);
    }else{
      limit = Math.floor(parseFloat(array_texts.length)/2.0);
    }
  }
  let compt = 0
  $("#content-viz .all_viz_details").each(function() {
     var div_id = $(this).attr('id');
     var string = $("#vzn"+div_id).val().toLowerCase().trim();
     var inc = 0;
     for(let i = 0; i < array_texts.length; i++){
       if(string.indexOf(array_texts[i]) != -1){
         inc = inc + 1
       }
     }
     if(inc >= limit){
       $(this).show();
       compt = compt + 1
     }else{
        $(this).hide();
     }
  });
  if($("#nbviz_tot")){
    $("#nbviz_tot").remove();
  }
  $('#content-viz').prepend("<p id='nbviz_tot'><i><b>" + gettext("Help us provide you better visualization by rating these visualizations.<br/>Nb Visualizations: ") + compt + "</b></i></p>");
}

function order_score(include_add_score=0){
  /*$('#content-viz').append($('#content-viz .all_viz_details').sort(function(a,b){
     id1 = a.getAttribute("id");
     id2 = b.getAttribute("id");
     val1 = -50;
     val2 = -50;
     if($("#sc"+id2).val() != ""){
       val2 = $("#sc"+id2).val();
     }
     if($("#sc"+id1).val() != ""){
       val1 = $("#sc"+id1).val();
     }

     if(include_add_score == 0){
       diff = parseInt(val2) - parseInt(val1);
     }else{
       diff = parseInt(val2) + parseInt($("#scmarg"+id2).val()) - parseInt(val1) - parseInt($("#scmarg"+id1).val());
     }
     return diff;
  }));*/
  $('.rate-viz').click();
  if($("#nbviz_tot")){
    $("#nbviz_tot").remove();
  }
  var action = $("#visualization_action").val();
  var nbviztot = tot_nb_vizs_recommend - tot_nb_vizs_deducted;
  if ($("#load-more").hasClass("hide")){
    nbviztot = $('#content-viz .all_viz_details').length;
  }
  if(action == "dist_recommend_viz"){
    $('#content-viz').prepend("<p id='nbviz_tot'><i><b>" + gettext("Help us provide you better visualization by rating these visualizations.<br/>Nb Distribution Visualizations: ") + nbviztot + "</b></i></p>");
  }else if(action == "empty_recommend_viz" && $("#is_task").val() == 0){
    $('#content-viz').prepend("<p id='nbviz_tot'><i><b>" + gettext("Help us provide you better visualization by rating these visualizations.<br/>Nb Analysis Visualizations: ") + nbviztot + "</b></i></p>");
  }else{
    $('#content-viz').prepend("<p id='nbviz_tot'><i><b>" + gettext("Help us provide you better visualization by rating these visualizations.<br/>Nb Visualizations: ") + nbviztot + "</b></i></p>");
  }
  if($('#content-viz .all_viz_details').length > 0){
    $(".no-viz").removeClass("hide");
  }else{
    $(".no-viz").addClass("hide");
  }
  if($("#content-viz .loader").length > 0){
    $(".se-pre-con").fadeIn("slow");
    $(".spinner-loading").fadeIn("slow");
    $("#loader").fadeIn("slow");
  }else{
    $(".se-pre-con").fadeOut("slow");
    $(".spinner-loading").fadeOut("slow");
    $("#loader").fadeOut("slow");
    $(".score").val("");
  }
}

function handle_viz_update(){
  if(list_type_viz_active.length <= 0){
    //init_viztypes();
    //list_type_viz_active = list_viz_show.slice();
    list_type_viz_active = [];
    list_viz_show = [];
    empty_type_viz = 1;
    handle_recommend_viz("recommend_viz1");
  }else{
    empty_type_viz = 0;
    if(list_type_viz_active.length > 0){
      $("#nb_viz").val(list_type_viz_active.length);
      var i = 0;
      can_run_next_viz_type = false;
      $("#submit_full_data").val(1);
      $("#type_viz").val(list_type_viz_active[i]);
      $("#visualization_action").val("update_viz");
      $("#visualization_code").val(generate_viz_code());
      $("#viz-form").submit();
    }else{
      M.toast({html: gettext("Please select at least one visualization type"), classes: 'red rounded', displayLength:10000});
    }
  }
}

function handle_change_viz(){
	empty_type_viz = 0;
	if(list_type_viz_active.length > 0){
	  $("#nb_viz").val(list_type_viz_active.length);
	  var i = 0;
	  can_run_next_viz_type = false;
	  $("#submit_full_data").val(1);
	  $("#type_viz").val(list_type_viz_active[i]);
	  $("#visualization_action").val("update_viz");
	  //$("#visualization_code").val(change_viz_code);
    $("#visualization_code").val(generate_viz_code());
	  $("#viz-form").submit();
	}else{
	  M.toast({html: gettext("Please select at least one visualization type"), classes: 'red rounded', displayLength:10000});
	}
}

function rate_viz(viz_code){
  if ($("#divsc"+viz_code).hasClass("hide")){
    $("#divsc"+viz_code).removeClass("hide");
    $('.starrr').starrr({
      max: 10,
      change: function(e, value){
        var lem = $("#"+e.target.id);
        var myid = lem.data('target');
        if(parseInt(value) == 1){
          $("#sc"+myid).val($("#bad_rate").val());
        }else{
          $("#sc"+myid).val(value);
        }
        submit_rate(viz_code)
      }
    });
  }else{
    //$("#divsc"+viz_code).addClass("hide");
  }
}

function submit_rate(viz_code){
  var viz_codes = [];
  var viz_scores = [];
  var viz_types = [];
  var viz_type_marks = [];
  var viz_score_settings = [];
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
  if(viz_codes.length > 0){
    $("#viz_codes").val(JSON.stringify(viz_codes));
    $("#viz_scores").val(JSON.stringify(viz_scores));
    $("#viz_types").val(JSON.stringify(viz_types));
    $("#viz_type_marks").val(JSON.stringify(viz_type_marks));
    $("#viz_score_settings").val(JSON.stringify(viz_score_settings));
    //$("#divsc"+viz_code).addClass("hide");
    $("#score-form").submit();
  }else{
    M.toast({html: gettext("Please assign rate"), classes: 'red rounded', displayLength:10000});
  }
}

function selectLayout(sel){
  $("#dash_layout").val(sel);
  if(parseInt(sel) == 12){
    $(".layout1").addClass("layoutSelected");
    $(".layout2").removeClass("layoutSelected");
  }else{
    $(".layout2").addClass("layoutSelected");
    $(".layout1").removeClass("layoutSelected");
  }
  $(".dhviz").each(function() {
  	if(parseInt(sel) == 12){
  		if (!$(this).hasClass("m12")){
  			$(this).removeClass("m6");
  			$(this).addClass("m12");
  		}
  	}else{
  		if (!$(this).hasClass("m6")){
  			$(this).removeClass("m12");
  			$(this).addClass("m6")
  		}
  	}
  });
  setTimeout(function() {
    resizeViz();
  }, 100);
}

function openCreate(){
  /*$("#graph-search").hide();
  emptyViz();*/
  var elem = document.querySelectorAll('#vizmarks-att')[0];
  var instance = M.Collapsible.getInstance(elem);
  instance.open(0);
  $("#textvizu").text(gettext("Create Visualization"));
  if($("#user_type").val().trim()=='non-expert' || $("#user_type").val().trim()=='intermediate'){
    $("#notadv-opt").trigger("click");
  }else{
    $("#adv-opt").trigger("click");
  }
  $('html,body').animate({
        scrollTop: $("#vizmarks-att").offset().top-35},
        'slow');
}

function initFiltDash(){
  $("#dash-filt .dash-filt").each(function() {
     $(this).remove();
  });
  $("#dash-filt"+'drop').show();
  if ($("#dash-filt"+'help').length) {
    $("#dash-filt"+'help').remove();
  }
  var nbcat = 0;
  $(".dim").each(function() {
     let myid = $(this).attr('id');
     var lem = $("#"+myid);
     var realtype = lem.data('realtype');
     if(realtype == 'date'){
       move(myid,'dash-filt');
     }
     if(nbcat == 0 && realtype == 'cat'){
       move(myid,'dash-filt');
       nbcat = nbcat + 1;
     }
  });
}


function data_content(file_code){
  if($("#vizmarks-att").hasClass("hide")){
  }else{
    $("#vizmarks-att").addClass("hide");
  }
  if(!$("#vizedit").hasClass("hide")){
    $("#vizedit").addClass("hide");
  }
  closeAlt();
  $("#graph-search").hide();
  let loader = $("#viz-loader").html();
  var div_all = '<div class="col loader s12" style="overflow: auto !important;" id="tb'+file_code+'">'+loader+'</div>';
  $('#content-viz').html(div_all);
  $("#res-title").html(gettext("Data Content"));
  if ($("#vizresults").hasClass("hide")){
      $("#vizresults").removeClass("hide");
  }

  var datacont = $.ajax({
    type: 'GET',
    url: '/data-content/'+file_code+"/",
    success: function(resultData) {
      $("#tb"+file_code).removeClass("loader");
      if (resultData.success) {
        $("#tb"+file_code).html(resultData.plot_table);
        $("#res-title").html(gettext("Data Content")+": "+resultData.title);
      }else{
        $("#tb"+file_code).remove();
      }
    },
    error:function(err) {
      $("#tb"+file_code).removeClass("loader");
      $("#tb"+file_code).remove();
      //$("#"+visualization_code).html("<p>"+gettext("Unable to display the plot")+"</p>");
    },
  });
}

function closeAlt(){
  is_alter_viz = 0;
  $('#content-viz .all_viz_details').removeClass("boxactive");
  $("#vizresults").removeClass("m8");
  $("#vizresults").removeClass("l8");
  $("#vizresults").addClass("m12");
  $("#vizresults").addClass("l12");
  $("#alternviztypes").addClass("hide");
  setTimeout(function() {
    resizeViz();
  }, 100);
}

function openAlt(){
  is_alter_viz = 1;
  $("#vizresults").removeClass("m12");
  $("#vizresults").removeClass("l12");
  $("#vizresults").addClass("m8");
  $("#vizresults").addClass("l8");
  $("#alternviztypes").removeClass("hide");
  setTimeout(function() {
    resizeViz();
  }, 100);
}

function removeViz(visualization_code){
  $("#"+visualization_code).remove();
}
