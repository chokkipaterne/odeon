var keys = [];
var columns = [];
var delete_code = ""
var inc_dt = 0;

function show_hide(){
  var proj_type = $("#project_type").val();
  $(".opths").addClass("hide");
  if (proj_type == "proposed"){
    $(".sp").removeClass("hide");
  }else if (proj_type == "external"){
    $(".ep").removeClass("hide");
  }else if (proj_type == "internal"){
    $(".ep").removeClass("hide");
    $('#status option').each(function () {
        if ($(this).hasClass('hide')) {
        }else{
    	    if($(this).val() != ''){
    			//$(this).prop("selected", true);
    			$(this).attr("selected","selected");
    			return false;
    		}
    	}
    });
  }
  if($('#status').find(":selected").hasClass("hide")){
    $('#status').val("");
  }
}

function interface_switch(chosen_opt){
  chosen_opt = parseInt(chosen_opt);
  if(chosen_opt == 1){
    $("#opendata").removeClass("hide");
    $("#spec-files").addClass("hide");
  }
  if(chosen_opt == 2){
    $("#spec-files").removeClass("hide");
    $("#opendata").addClass("hide");
  }
}

function toogle_preprocess(){
  if ($("#pre-cont").hasClass("hide")){
    $("#pre-cont").removeClass("hide");
  }else{
    $("#pre-cont").addClass("hide");
  }
}
function togglepdesc(pid){
  $("#pdesc1_"+pid).toggleClass("hide");
  $("#pdesc2_"+pid).toggleClass("hide");
}

//Delete file function
function deleteFile(code){
  $("#file_code").val(code);
  delete_code = code
  $("#"+delete_code).addClass("hide");

  if($("#view_file_code").val() == code){
    $("#view_file").addClass("hide");
  }else if($("#edit_file_code").val() == code){
    $("#view_file").addClass("hide");
  }
  $("#delete-file-form").submit();
}

//View file function
function viewFile(code){
  $("#view_file_code").val(code);
  $("#action_type").val("view");
  $("#view-file-form").submit();
}

function editDataInfo(code){
  $("#edit_file_code").val(code);
  $("#edit-file-form").submit();
}

//Select file from demo
function selectFile(code){
  $("#file_selected").val(code);
  $("#loaddata-form").submit();
}

//Call External link submit
function externalLink(){
  $("#external-form").submit();
}

//Call New project submit
function createProject(){
  //var r = confirm(gettext("Are you sure to create a new project?"));
  //if (r == true) {
  $("#createproject-form").submit();
  //}
}

//Open Load project modal
function openModalProject(){
  var elem = document.querySelectorAll('#modalLoadProject')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}

//Update number of files selected
function updateNbFiles(){
  var nbb_files = $("#nbfiles").text();
  var user_type = $("#user_type").val();
  user_type = user_type.trim();
  nbb_files = parseInt(nbb_files);
  $("#obj_transf").val("");
  $(".transf").addClass("hide");
  $("#text-trans").text(gettext("Get started by choosing your transformation"));
  /*if(user_type == "expert"){
    $(".preprocess").removeClass("hide");
  }else{
    $(".preprocess").addClass("hide");
  }*/
  if(nbb_files > 1){
    $("#cmbdat").removeClass("hide");
  }else{
    $("#cmbdat").addClass("hide");
  }
  if(nbb_files > 0){
    $(".checkhide").removeClass("hide");
    if(user_type == "non-expert"){
      //$(".select-files").addClass("hide");
      $("#text-top").text(gettext("Add Data to Project"));
    }
  }
  if(nbb_files == 0){
    $(".checkhide").addClass("hide");
    if(user_type == "non-expert"){
      //$(".select-files").removeClass("hide");
      $("#text-top").text(gettext("Add Data to Project"));
    }
  }
}

//Get all datasets based on user request
function getDatasets(){
    var obj_portal = $("#obj_portal").val();
    var obj_dataset = $('#obj_dataset').val();
    if (obj_portal != "" && obj_dataset != ""){
      $("#portal").val(obj_portal);
      $("#dataset").val(obj_dataset);
      var $form = $("#opd-form");
      url = $form.attr("action");
      mydata = $form.serialize();
      var viewViz = $.ajax({
          type: 'POST',
          url: url,
          data: mydata,
          success: function(resultData) {
            inc_dt = 0;
            if (resultData.success) {
              console.log(resultData.data);
              show_datasets(resultData);
            }else{
              total_count = '<p class="center"><b><i>'+gettext("Total datasets: 0")+"</i></b></p>";
              $("#opd-cont").html(total_count);
              $("#opd-back").html("");
              $("#opd-more").html("");
              M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
            }
          },
          error:function(err) {
            M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
          },
      });
    }else{
      if(obj_dataset != ""){
        M.toast({html: gettext("Please fill all fields"), classes: 'red rounded', displayLength:10000});
      }
    }
}

//Handle load more dataset button
function load_more_opd(){
  $("#opd-more").html("");
  var $form = $("#next-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var viewViz = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(resultData) {
        if (resultData.success) {
          console.log(resultData.data);
          show_datasets(resultData, 1);
        }else{
          M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
        }
      },
      error:function(err) {
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
  });
}

//Trancate string
function truncateString(str, num) {
  if(!str || str.length == 0){
    return ""
  }
  if (str.length <= num) {
    return str
  }
  return str.slice(0, num) + '...'
}

//Handle display of List datasets
function show_datasets(results, init=0){
  mydata = results["data"];
  current_platform = results["current_platform"];
  if(init == 0){
    total_count = '<p class="center"><b><i>'+gettext("Total datasets: ")+mydata["total_count"]+"</i></b></p>";
    $("#opd-cont").html(total_count);
    $("#opd-back").html("");
  }
  $("#opd-more").html("");
  if(current_platform == "1" || current_platform == "2"){
    if(current_platform == "2"){
      total_count = '<p class="center"><b><i>'+gettext("Total datasets: ")+mydata["total_count"]+"</i></b></p>";
      $("#opd-cont").html(total_count);
    }
    explore_link = results["explore_link"];
    display_datasets(mydata, explore_link, current_platform);
  }
}

//Remove html tags from string
function strip_html_tags(str)
{
   if ((str===null) || (str===''))
       return false;
  else
   str = str.toString();
  return str.replace(/<[^>]*>/g, '');
}

//Opendasoft display style
function display_datasets(mydata, explore_link, current_platform){
  var incc = 0;
  datasets = mydata["datasets"]
  for(incc=0; incc < datasets.length; incc++){
    dataset_id = datasets[incc]["dataset"]["dataset_id"];
    title = datasets[incc]["dataset"]["metas"]["default"]["title"];
    description = "";
    if(datasets[incc]["dataset"]["metas"]["default"]["description"]){
      description = datasets[incc]["dataset"]["metas"]["default"]["description"];
    }
    modified=""
    records_count = ""
    if(datasets[incc]["dataset"]["metas"]["default"]["modified"]){
      modified = datasets[incc]["dataset"]["metas"]["default"]["modified"];
      modified = modified.substring(0,19).replace(/T/g, " ");
    }
    if(datasets[incc]["dataset"]["metas"]["default"]["records_count"]){
      records_count = datasets[incc]["dataset"]["metas"]["default"]["records_count"];
    }
    description = description.replace(/<p>/g, "");
    description = description.replace(/<\/p>/g, "");
    expl_link = "";
    if (current_platform == "1"){
      expl_link = explore_link.replace(/#dt_id#/g, dataset_id);
    }else if (current_platform == "2"){
      package_id = datasets[incc]["dataset"]["package_id"];
      expl_link = explore_link.replace(/#pack_id#/g, package_id);
      expl_link = expl_link.replace(/#res_id#/g, dataset_id);
    }

    elem = '<div class="col l6 m6 s12"><div class="boxed">'
    elem += '<b><a target="_blank" href="'+expl_link+'">'+truncateString(title, 50)+'</a></b>'
    elem += '<br/>'+truncateString(strip_html_tags(description), 100)
    if(records_count != ""){
      elem += '<br/><span class="smalltxt">'+gettext("Records Count: ")+records_count+'</span>'
    }else{
      elem += '<br/><span class="smalltxt">&nbsp;</span>';
    }
    if(modified != ""){
      elem += '<br/><span class="smalltxt">'+gettext("Modified: ")+modified+'</span>';
    }else{
      elem += '<br/><span class="smalltxt">&nbsp;</span>';
    }
    elem += '<br/><div><a class="btn-flat waves-effect waves-light green darken-1 right lower white-text" href="javascript:void(0)" onclick="select_opd(\''+dataset_id+'\',\''+inc_dt+'\')">'+gettext("Select")+'</a>'
    elem += '<a target="_blank" class="btn-flat waves-effect waves-light blue darken-1 right lower white-text" href="'+expl_link+'">'+gettext("Explore")+'</a></div>'
    elem += '<div class="clear"></div></div></div>'
    $("#opd-cont").append(elem);
    inc_dt = inc_dt + 1
  }

  links = mydata["links"]
  for(incc=links.length-1; incc > 0 ; incc--){
    current_link = links[incc];
    if(current_link["rel"] == "next"){
      link_next = current_link["href"];
      $("#link_next").val(link_next);
      elem = '<a class="btn waves-effect waves-light indigo darken-1 center lower white-text" href="javascript:void(0)" onclick="load_more_opd()">'+gettext("Load more")+'</a>'
      elem += '<div class="clear"></div>'
      $("#opd-more").append(elem);
      break;
    }

  }
}

function dynamic_data_li(code,file_link, view_link,title,quality){
  var hidept = "hide";
  var current_project_type = $("#current_project_type").val().trim();
  if(current_project_type == 'internal'){
    hidept = ""
  }
  arr_link = view_link.split("/")
  view_link = "/get-started?explore_file="+arr_link[arr_link.length-1]
  window.location.href = view_link;
  var element = '<li id="'+code+'" class="collection-item file no-pad">';
  element += "<div class='truncate'>";
  element += "<a target='_blank' href='"+file_link+"'>"+title+"</a> <small class='"+hidept+"'>"+quality+"</small>";
  element += '<a onclick="deleteFile(\''+code+'\')" href="javascript:void(0)" data-code="'+code+'" class="btn-flat waves-effect waves-light red darken-1 rounded lower secondary-content delete tooltipped white-text" data-position="top" data-tooltip="'+gettext("Delete Data")+'"><i class="material-icons left">delete</i> '+gettext("Delete")+'</a>';
  element += '<a href="'+view_link+'" class="btn-flat waves-effect waves-light green darken-1 rounded lower secondary-content view tooltipped white-text" data-position="top" data-tooltip="'+gettext("Explore Data")+'" data-code="'+code+'" href="javascript:void(0)""><i class="material-icons left">info</i> '+gettext("Explore")+'</a>';
  //element += '<a onclick="editDataInfo(\''+code+'\')" class="'+hidept+' btn-flat waves-effect waves-light indigo darken-1 rounded lower secondary-content edit-info tooltipped white-text" data-position="top" data-tooltip="'+gettext("Adjust Column Datatype and Information")+'" data-code="'+code+'" href="javascript:void(0)""><i class="material-icons left">edit</i> '+gettext("Edit")+'</a>';
  element += '</div></li>';
  return element
}

//Handle when user cliks on select dataset
function select_opd(dataset_id, dataset_inc){
  $("#dataset_id").val(dataset_id);
  $("#dataset_inc").val(dataset_inc);
  $("#loader").removeClass("hide");

  var $form = $("#getopd-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var getopd = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(data) {
        //console.log(data);
        if (data.is_valid) {
          var elem = document.querySelectorAll('.list_data')[0];
          var instance = M.Collapsible.getInstance(elem);
          instance.open(0);
          $("#nbfiles").text(data.nbfiles);
          var code = data.code;
          var file_link = data.file_link;
          var title = data.full_title;
          var quality = gettext("(Data Quality: ")+data.quality+"%)"
          var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code

          var element = dynamic_data_li(code,file_link,view_link,title,quality);
          $("#list-files").append(element);
          $('.tooltipped').tooltip();
          M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
        }else{
          M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
        }
        updateNbFiles();
      },
      error:function(err) {
        $("#loader").addClass("hide");
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        updateNbFiles();
      },
  });
}

//Get all datasets to list in dropdown
function get_all_datasets(cdt_id, cdt_id1=''){
  $('#'+cdt_id).html("<option value=''>"+gettext("Select Data")+"</option>");
  if(cdt_id1 != ''){
    $('#'+cdt_id1).html("<option value=''>"+gettext("Select Data")+"</option>");
  }
  var $form = $("#alldata-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var getopd = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(data) {
        //console.log(data);
        keys = data.keys;
        mydata = data.data
        var list_options ="<option value=''>"+gettext("Select Data")+"</option>";
        for (i = 0; i < keys.length; i++) {
          list_options += "<option value='" + keys[i] + "'>" + mydata[keys[i]]["full_title"] + "</option>";
        }
        //console.log(list_options);
        //console.log(cdt_id);
        $("#"+cdt_id).html(list_options);
        $("#"+cdt_id).select2();
        //$("#"+cdt_id).val("").trigger('change');
        if(cdt_id1 != ''){
          $("#"+cdt_id1).html(list_options);
          $("#"+cdt_id1).select2();
          //$("#"+cdt_id1).val("").trigger('change');
          $("#"+cdt_id).on('change', function(e) {
             var se_val = $("#"+cdt_id).val();
             get_dataset_columns(cdt_id,se_val,0);
          });
          $("#"+cdt_id1).on('change', function(e) {
             var se_val = $("#"+cdt_id1).val();
             get_dataset_columns(cdt_id1,se_val,0);
          });
          ccol_id = cdt_id.replace(/dt/g, "col");
          $('#'+ccol_id).html("");
          $("#"+ccol_id).select2();
          //$("#"+ccol_id).val("").trigger('change');
          ccol_id1 = cdt_id1.replace(/dt/g, "col");
          $('#'+ccol_id1).html("");
          $("#"+ccol_id1).select2();
          //$("#"+ccol_id1).val("").trigger('change');
        }else{
          $("#"+cdt_id).on('change', function(e) {
             var se_val = $("#"+cdt_id).val();
             get_dataset_columns(cdt_id,se_val,0);
          });
          ccol_id = cdt_id.replace(/dt/g, "col");
          $('#'+ccol_id).html("");
          $("#"+ccol_id).select2();
          //$("#"+ccol_id).val("").trigger('change');
        }

        if (!data.success) {
          M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
        }
      },
      error:function(err) {
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
  });
}

// Get columns of datasets
function get_dataset_columns(cdt_id, data_code, multi=1){
  ccol_id = cdt_id.replace(/dt/g, "col");
  $('#'+ccol_id).html("");

  if(data_code == ""){
    $("#"+ccol_id).select2();
    return 1;
  }
  $("#col_code").val(ccol_id);

  $("#data_code").val(data_code);
  var $form = $("#datacol-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var getopd = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(data) {
        //console.log(data);
        keys = data.keys;
        var list_options ="";
        if(multi==1){
          list_options ="";
        }
        labels = data.fulldata
        for (i = 0; i < keys.length; i++) {
          list_options += "<option value='" + keys[i] + "'>" + labels[keys[i]]["fulllabel"] + "</option>";
        }
        $("#"+ccol_id).html(list_options);
        $("#"+ccol_id).select2();
        if (!data.success) {
          M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
        }
      },
      error:function(err) {
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
  });
}

function combdata(){
  var combdata_dt1 = $("#combdata_dt1").val();
  var combdata_col1 = $("#combdata_col1").val();
  var combdata_rel = $("#combdata_rel").val();
  var combdata_dt2 = $("#combdata_dt2").val();
  var combdata_col2 = $("#combdata_col2").val();
  var combdata_dtname = $("#combdata_dtname").val();

  var h_combdata_col1 = "";
   for(incc=0; incc < combdata_col1.length; incc++){
     h_combdata_col1 += combdata_col1[incc]+"##"
   }
   $("#h_combdata_col1").val(h_combdata_col1);

   var h_combdata_col2 = "";
   for(incc=0; incc < combdata_col2.length; incc++){
     h_combdata_col2 += combdata_col2[incc]+"##"
   }
   $("#h_combdata_col2").val(h_combdata_col2);

  if(!combdata_dt1 || !combdata_col1 || !combdata_dt2 || !combdata_col2 || !combdata_dtname){
    M.toast({html: gettext("Please fill all fileds."), classes: 'red rounded', displayLength:10000});
    return 1;
  }
  if(combdata_col2.length != combdata_col1.length){
    M.toast({html: gettext("You should choose the same number of columns in both side."), classes: 'red rounded', displayLength:10000});
  }
  if(combdata_dt1 == combdata_dt2){
    M.toast({html: gettext("Please choose different datasets."), classes: 'red rounded', displayLength:10000});
    return 1;
  }

  var $form = $("#combdata-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var getopd = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(data) {
        console.log(data);
        if (data.is_valid) {
          var elem = document.querySelectorAll('.list_data')[0];
          var instance = M.Collapsible.getInstance(elem);
          instance.open(0);
          $("#nbfiles").text(data.nbfiles);
          var code = data.code;
          var file_link = data.file_link;
          var title = data.full_title;
          var quality = gettext("(Data Quality: ")+data.quality+"%)"
          var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code

          var element = dynamic_data_li(code,file_link,view_link,title,quality);
          $("#list-files").append(element);
          $('.tooltipped').tooltip();
          M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
          updateNbFiles();
        }else{
          M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
        }
      },
      error:function(err) {
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
  });
}


function dropcol(){
  var dropcol_dt = $("#dropcol_dt").val();
  var dropcol_col = $("#dropcol_col").val();
  var dropcol_dtname = $("#dropcol_dtname").val();
  var h_dropcol_col = "";
  for(incc=0; incc < dropcol_col.length; incc++){
    h_dropcol_col += dropcol_col[incc]+"##"
  }
  $("#h_dropcol_col").val(h_dropcol_col);

  if(!dropcol_dt || !dropcol_col){
    M.toast({html: gettext("Please fill all fileds."), classes: 'red rounded', displayLength:10000});
    return 1;
  }

  var $form = $("#dropcol-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var getopd = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(data) {
        console.log(data);
        if (data.is_valid) {
          var elem = document.querySelectorAll('.list_data')[0];
          var instance = M.Collapsible.getInstance(elem);
          instance.open(0);
          if(!dropcol_dtname || dropcol_dtname==""){
            $("#"+dropcol_dt).remove();
            if($("#view_file_code").val() == dropcol_dt){
            	$("#view_file").addClass("hide");
            }
          }
          $("#nbfiles").text(data.nbfiles);
          var code = data.code;
          var file_link = data.file_link;
          var title = data.full_title;
          var quality = gettext("(Data Quality: ")+data.quality+"%)"
          var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code;

          var element = dynamic_data_li(code,file_link,view_link,title,quality);
          $("#list-files").append(element);
          $('.tooltipped').tooltip();
          M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
          updateNbFiles();
        }else{
          M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
        }
      },
      error:function(err) {
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
  });
}

function repval(){
  var repval_dt = $("#repval_dt").val();
  var repval_col = $("#repval_col").val();
  var repval_search = $("#repval_search").val();
  var repval_rep = $("#repval_rep").val();
  var repval_dtname = $("#repval_dtname").val();
  var h_repval_col = "";
  for(incc=0; incc < repval_col.length; incc++){
    h_repval_col += repval_col[incc]+"##"
  }
  $("#h_repval_col").val(h_repval_col);

  if(!repval_dt || !repval_col || !repval_rep){
    M.toast({html: gettext("Please fill all fileds."), classes: 'red rounded', displayLength:10000});
    return 1;
  }

  var $form = $("#repval-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var getopd = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(data) {
        console.log(data);
        if (data.is_valid) {
          var elem = document.querySelectorAll('.list_data')[0];
          var instance = M.Collapsible.getInstance(elem);
          instance.open(0);
          if(!repval_dtname || repval_dtname==""){
            $("#"+repval_dt).remove();
            if($("#view_file_code").val() == repval_dt){
            	$("#view_file").addClass("hide");
            }
          }
          $("#nbfiles").text(data.nbfiles);
          var code = data.code;
          var file_link = data.file_link;
          var title = data.full_title;
          var quality = gettext("(Data Quality: ")+data.quality+"%)";
          var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code;

          var element = dynamic_data_li(code,file_link,view_link,title,quality);
          $("#list-files").append(element);
          $('.tooltipped').tooltip();
          M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
          updateNbFiles();
        }else{
          M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
        }
      },
      error:function(err) {
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
  });
}

function aggdata(){
  var aggdata_dt = $("#aggdata_dt").val();
  var aggdata_col = $("#aggdata_col").val();
  var aggdata_dtname = $("#aggdata_dtname").val();
  var h_aggdata_col = "";
  for(incc=0; incc < aggdata_col.length; incc++){
    h_aggdata_col += aggdata_col[incc]+"##"
  }
  $("#h_aggdata_col").val(h_aggdata_col);

  if(!aggdata_dt || !aggdata_col){
    M.toast({html: gettext("Please fill all fileds."), classes: 'red rounded', displayLength:10000});
    return 1;
  }

  var $form = $("#aggdata-form");
  url = $form.attr("action");
  mydata = $form.serialize();
  var getopd = $.ajax({
      type: 'POST',
      url: url,
      data: mydata,
      success: function(data) {
        console.log(data);
        if (data.is_valid) {
          var elem = document.querySelectorAll('.list_data')[0];
          var instance = M.Collapsible.getInstance(elem);
          instance.open(0);
          if(!aggdata_dtname || aggdata_dtname==""){
            $("#"+aggdata_dt).remove();
            if($("#view_file_code").val() == aggdata_dt){
            	$("#view_file").addClass("hide");
            }
          }
          $("#nbfiles").text(data.nbfiles);
          var code = data.code;
          var file_link = data.file_link;
          var title = data.full_title;
          var quality = gettext("(Data Quality: ")+data.quality+"%)"
          var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code;


          var element = dynamic_data_li(code,file_link,view_link,title,quality);
          $("#list-files").append(element);
          $('.tooltipped').tooltip();
          M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
          updateNbFiles();
        }else{
          M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
        }
      },
      error:function(err) {
        M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
      },
  });
}

//hide or show project description
function hs_plink(){
  var val = $("#project_type").val();
  $("#current_project_type").val(val);
  if (val == 'external'){
    $("#plink").removeClass("hide");
    $("#project_link").prop('required',true);
  }else{
    $("#plink").addClass("hide");
    $("#project_link").prop('required',false);
  }
  if (val == "internal"){
    $("#ldt").addClass("hide");
  }else{
    $("#ldt").removeClass("hide");
  }
  show_hide();
}

//Load project from the list of projects
function loadP(p_code){
  $("#project_code").val(p_code);
  $("#loadproject-form").submit();
}

$(document).ready(function() {
  $('.tabs').tabs();
  if($("#project_type").length){
    hs_plink();
  }
  $("#obj_portal").select2({
      tags: true,
      createTag: function (params) {
        var term = $.trim(params.term);
        if (term === '') {
          return null;
        }
        return {
          id: term,
          text: term,
          newTag: true // add additional parameters
        }
      }
  });
  $("#obj_portal").on('change', function(e) {
     getDatasets();
  });
  $('#obj_dataset').keypress(function(event){
      var keycode = (event.keyCode ? event.keyCode : event.which);
      if(keycode == '13'){
        getDatasets();
      }
      //Stop the event from propogation to other handlers
      //If this line will be removed, then keypress event handler attached
      //at document level will also be triggered
      event.stopPropagation();
  });
});

$(function(){
  $(document).ready(function(){
    updateNbFiles();
  });
  $('#modalLoad').modal();
  $('#modalLoadProject').modal();
  $('#modalExternal').modal();

  //Submit file slected to backend
  $("#loaddata-form").on("submit", function(event) {
      event.preventDefault();
      var elem = document.querySelectorAll('#modalLoad')[0];
      var instance = M.Modal.getInstance(elem);
      instance.close();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      var loadFile = $.ajax({
          type: 'POST',
          url: url,
          data: mydata,
          success: function(data) {
            console.log(data);
            if (data.is_valid) {
              var elem = document.querySelectorAll('.list_data')[0];
              var instance = M.Collapsible.getInstance(elem);
              instance.open(0);
              $("#nbfiles").text(data.nbfiles);
              var code = data.code;
              var file_link = data.file_link;
              var title = data.full_title;
              var quality = gettext("(Data Quality: ")+data.quality+"%)";
              var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code;


              var element = dynamic_data_li(code,file_link,view_link,title,quality);
              $("#list-files").append(element);
              $('.tooltipped').tooltip();
              M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
            }else{
              M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
            }
            updateNbFiles();
          },
          error:function(err) {
            M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
            updateNbFiles();
          },
    });
  });

  //Submit external link data to backend
  $("#external-form").on("submit", function(event) {
      event.preventDefault();
      var elem = document.querySelectorAll('#modalExternal')[0];
      var instance = M.Modal.getInstance(elem);
      instance.close();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      var loadFile = $.ajax({
          type: 'POST',
          url: url,
          data: mydata,
          success: function(data) {
            console.log(data);
            if (data.is_valid) {
              $('#external-form')[0].reset();
              var elem = document.querySelectorAll('.list_data')[0];
              var instance = M.Collapsible.getInstance(elem);
              instance.open(0);
              $("#nbfiles").text(data.nbfiles);
              var code = data.code;
              var file_link = data.file_link;
              var title = data.full_title;
              var quality = gettext("(Data Quality: ")+data.quality+"%)";
              var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code;


              var element = dynamic_data_li(code,file_link,view_link,title,quality);
              $("#list-files").append(element);
              $('.tooltipped').tooltip();
              M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
            }else{
              var elem = document.querySelectorAll('#modalExternal')[0];
              var instance = M.Modal.getInstance(elem);
              instance.open();
              M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
            }
            updateNbFiles();
          },
          error:function(err) {
            var elem = document.querySelectorAll('#modalExternal')[0];
            var instance = M.Modal.getInstance(elem);
            instance.open();
            M.toast({html: gettext("Please check your inputs"), classes: 'red rounded', displayLength:10000});
            updateNbFiles();
          },
    });
  });

  //Submit delete form to backend
  $("#delete-file-form").on("submit", function(event) {
      event.preventDefault();
      var code = $("#file_code").val();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      var deleteFile = $.ajax({
          type: 'POST',
          url: url,
          data: mydata,
          success: function(resultData) {
            if (resultData.deleted) {
              $("#nbfiles").text(resultData.nbfiles);
              $("#"+delete_code).remove();
              M.toast({html: resultData.message, classes: 'green rounded', displayLength:2000});
            }else{
              $("#"+delete_code).removeClass("hide");
              M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
            }
            updateNbFiles();
          },
          error:function(err) {
            $("#"+code).removeClass("hide");
            M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
            updateNbFiles();
          },
    });
  });

  //Submit edit file code to get edit data form
  $("#edit-file-form").on("submit", function(event) {
      var title = "text"
      event.preventDefault();
      var code = $("#edit_file_code").val();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      $("#view_file").addClass("hide");
      var editFile = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            $("#view_file").removeClass("hide");
            $("#content_editdata").html(resultData.form);
            title = resultData.title;
            $("#file_name").html(title);
            if(resultData.message){
              M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
            }
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
        },
        error:function(err) {
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
      });
    });


  //Submit view file selected on backend
  $("#view-file-form").on("submit", function(event) {
      var title = "text"
      event.preventDefault();
      var code = $("#view_file_code").val();
      var $form = $(this),
      url = $form.attr("action");
      mydata = $form.serialize();
      $("#view_file").addClass("hide");
      var deleteFile = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            $("#view_file").removeClass("hide");
            $("#content_view_file").html(resultData.plot_table);
            var user_type = $("#user_type").val();
            user_type = user_type.trim();
            if(user_type == "expert"){
              $(".datasummary").removeClass("hide");
            }else{
              $(".datasummary").addClass("hide");
            }
            keys = resultData.keys;
            columns = resultData.columns;
            title = resultData.title;
            var list_options ="<option value=''>"+gettext("Select Column")+"</option>";
            for (i = 0; i < keys.length; i++) {
              list_options += "<option value='" + keys[i] + "'>" + keys[i] + "</option>";
            }
            $("#column_data").html(list_options);
            $("#datatypes").hide();
            $("#type_data").val("");
            $("#file_name").html(title+" <small>"+gettext("(Only the first 50 rows & 10 first columns)")+"</small>");
            if(resultData.message){
              M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
            }
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
        },
        error:function(err) {
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
      });
    });
});

$(function () {
  //Update datatype based on column
  $("#column_data").change(function() {
    var val = $("#column_data").val();
    if(val){
      $("#type_data").val(columns[val])
    }
  });

  //Show or hide data summary div
  $(".datasummary").click(function() {
    if($('#datatypes').css('display') != 'none'){
      $("#datatypes").hide();
      $(".transformData").addClass("hide");
    }else{
      $("#datatypes").show("slow");
      $(".transformData").removeClass("hide");
    }
  });

  //Change datatype
  $(".changeType").click(function() {
    $("#action_type").val("transform");
    $("#view-file-form").submit();
  });

  //submit edit data form
  $(".saveDataInfo").click(function() {
      var data_title = $("#data_title").val();
      if(!data_title || data_title == "" || data_title.length == 0){
        M.toast({html: gettext("Fields marked with * are mandatory."), classes: 'red rounded', displayLength:10000});
        return 0;
      }
      var $form = $("#edit-datainfo"),
      url = $form.attr("action");
      mydata = $form.serialize();
      var saveInfo = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            title = resultData.title;
            code = resultData.code;
            quality = resultData.quality;
            $("#file_name").html(title);
            $("#"+code+" a:first").html(title);
            $("#"+code+" small:first").html('(Data Quality:  '+quality+'%)');
            $("#view_file").addClass("hide");
            M.toast({html: resultData.message, classes: 'green rounded', displayLength:2000});
          }else{
            M.toast({html: resultData.message, classes: 'red rounded', displayLength:10000});
          }
        },
        error:function(err) {
          M.toast({html: gettext("Something went wrong"), classes: 'red rounded', displayLength:10000});
        },
      });

  });

  /* 1. OPEN THE FILE EXPLORER WINDOW */
  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });

  /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
  $("#fileupload").fileupload({
    dataType: 'json',
    sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */
    start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
      var strProgress = "0%";
      $("#progress-file").removeClass("hide");
      $("#progress-file-percent").css({"width": strProgress});
      $("#progress-file-text").text(strProgress);
    },
    stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINALIZE, HIDE THE MODAL */
      var strProgress = "0%";
      $("#progress-file-percent").css({"width": strProgress});
      $("#progress-file-text").text(strProgress);
      $("#progress-file").addClass("hide");
    },
    progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
      var progress = parseInt(data.loaded / data.total * 100, 10);
      var strProgress = progress + "%";
      console.log(strProgress);
      $("#progress-file-percent").css({"width": strProgress});
      $("#progress-file-text").text(strProgress);
    },
    done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
      if (data.result.is_valid) {
        var elem = document.querySelectorAll('.list_data')[0];
        var instance = M.Collapsible.getInstance(elem);
        instance.open(0);
        $("#nbfiles").text(data.result.nbfiles);
        var code = data.result.code;
        var file_link = data.result.file_link;
        var title = data.full_title;
        var quality = gettext("(Data Quality: ")+data.quality+"%)";
        var view_link = "/explore-data/"+($("#current_project_code").val()).trim()+"/"+code;

        var element = dynamic_data_li(code,file_link,view_link,title,quality);
        $("#list-files").append(element);
        $('.tooltipped').tooltip();
        M.toast({html: data.result.message, classes: 'green rounded', displayLength:2000});
      }else{
        M.toast({html: data.result.message, classes: 'red rounded', displayLength:10000});
      }
      updateNbFiles();
    }
  });

  $(".next").click(function() {
    let url = $(this).data('url');
    var numItems = $('.file').length
    if(numItems > 0){
      window.location.href = url;
    }else{
      M.toast({html: gettext("Please first upload data"), classes: 'red rounded', displayLength:10000});
    }
  });

  $(".previous").click(function() {
    let url = $(this).data('url');
    window.location.href = url;
  });

  //Handle when user chooses transformation
  $('#obj_transf').change(function() {
    var val = $("#obj_transf").val();
    $(".transf").addClass("hide");
    if(val != ""){
      text = $("#obj_transf").find("option:selected").text();
      $("#text-trans").text(text);
      $("#"+val).removeClass("hide");

      if(val=='dropcol'){
        $("#dropcol_dtname").val("");
        get_all_datasets('dropcol_dt');
      }else if(val=='repval'){
        $("#repval_search").val("");
        $("#repval_rep").val("");
        $("#repval_dtname").val("");
        get_all_datasets('repval_dt');
      }else if(val=='combdata'){
        $("#combdata_dtname").val("");
        get_all_datasets('combdata_dt1', 'combdata_dt2');
      }else if(val=='aggdata'){
        $("#aggdata_dtname").val("");
        get_all_datasets('aggdata_dt');
      }
    }else{
      $("#text-trans").text(gettext("Get started by choosing your transformation"));
    }
  });

  $('#project_type').change(function() {
    hs_plink();
  });
  $("#country").on('change', function(e) {
     generate_states("country", "project_state");
  });
  $("#country").trigger('change');
  $("#project_title").keydown(function( event ) {
    if ( event.which == 13 ) {
     event.preventDefault();
    }
    generate_titles("project_title",$("#project_title").val(),"project");
  });
  $("#project_title").bind("paste", function(e){
      value = e.originalEvent.clipboardData.getData('text');
      generate_titles("project_title",value,"project", true);
  });
});

/////////////////////Functions for data content and column overview and data quality
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
                divcol = '<div class="colexp col s12 m6" id="'+id+'"><a class="closediv" href="javascript:void(0)" onclick="removediv(\''+id+'\')">X</a>'+div_content+'</div>'
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
       $('.tabs').tabs('select','qcoverv');
  	  });
    }
    var nbopt = 0;
    $('#col option').each(function () {
    	var valth = $(this).first().attr("value");;
    	if (nbopt < 5 && valth != ""){
    		//$("#col").val(valth).trigger("change");
        change_col(valth);
    		sleep(200);
    	}
      if(nbopt == 5){
        //$("#col").val("").trigger("change");
        //change_col(val)
      }
    	nbopt = nbopt + 1;
    });
  }, 2000);
});

//Remove data distribution div
function removediv(id){
  $("#"+id).remove();
}

function change_col(val){
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
      mydata = mydata + val
      //console.log(mydata);
      var viewViz = $.ajax({
          type: 'POST',
          url: url,
          data: mydata,
          success: function(resultData) {
            if (resultData.success) {
              div_content = resultData.div_content
              divcol = '<div class="colexp col s12 m6" id="'+id+'"><a class="closediv" href="javascript:void(0)" onclick="removediv(\''+id+'\')">X</a>'+div_content+'</div>'
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
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

//Hide or show data quality graph or table
function togglediv(){
  $("#dqlt").toggleClass("hide");
  $("#tqlt").toggleClass("hide");
}
