//Variable globalses
var prev_title_proj = "-1";
var prev_title_dat = "-1";

//Autocomple function
function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        //if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
        if(arr[i].toUpperCase().indexOf(val.toUpperCase()) !== -1){
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          //b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          //b.innerHTML += arr[i].substr(val.length);
          b.innerHTML = arr[i]
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
              if(inp.id == "state"){
                $("#search-form").submit();
              }
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}

function generate_states(country_id, state_id){
  var $form = $("#state-form"),
  url = $form.attr("action");
  mydata = $form.serialize();
  if($("#"+country_id).val() != ""){
    $("#sch_country").val($("#"+country_id).val())
    var stateForm = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            json_data = resultData["states"]
            autocomplete(document.getElementById(state_id), json_data);
          }
        },
        error:function(err) {
        },
    });
  }
}

function generate_titles(obj_id, auto_search, auto_type, special){
  $("#auto_search").val(auto_search);
  $("#auto_type").val(auto_type);
  var $form = $("#autocomplete-form"),
  url = $form.attr("action");
  mydata = $form.serialize();
  var canrun = 1;
  console.log(mydata);
  if(auto_search != "" && auto_search.length >=2){
    if(auto_type == "project"){
      if(auto_search.toUpperCase().indexOf(prev_title_proj.toUpperCase()) !== -1){
        canrun = 0;
      }
      prev_title_proj = auto_search;
    }else{
      if(auto_search.toUpperCase().indexOf(prev_title_dat.toUpperCase()) !== -1){
        canrun = 0;
      }
      prev_title_dat = auto_search;
    }
  }
  console.log(canrun);
  if(auto_search != "" && (auto_search.length >=2 && canrun)){
    var autoForm = $.ajax({
        type: 'POST',
        url: url,
        data: mydata,
        success: function(resultData) {
          if (resultData.success) {
            json_data = resultData["datas"]
            autocomplete(document.getElementById(obj_id), json_data);
          }
        },
        error:function(err) {
        },
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
              M.toast({html: "Thank for supporting this project", classes: 'green rounded', displayLength:2000});
            }else{
              M.toast({html: "Thank for supporting this dataset", classes: 'green rounded', displayLength:2000});
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
              M.toast({html: "Add to favorites successfully.", classes: 'green rounded', displayLength:2000});
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

//Handle modal for request data
function modal_resquest_data(requested_data_pcode=''){
  $('#requested-form')[0].reset();
  if(requested_data_pcode!=""){
    $("#requested_data_pcode").val(requested_data_pcode);
  }
  var elem = document.querySelectorAll('#modalRequested')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}

function modal_subscribe_data(){
  $('#wr-form')[0].reset();
  var elem = document.querySelectorAll('#modalwr')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}

//Handle submit button for modal request data
function requestData(){
  $("#requested-form").submit();
}

//handle share dash button
function share_dash(dash_code="", file_code=""){
  //$("#dash_code").val("");
  weblink = $("#weblink").val();
  $("#message").val(gettext("Hi, you might be interested in the following project: ")+weblink+dash_code);

  var elem = document.querySelectorAll('#modalShare')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
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

//Go to specific section after page loads
function gotosection(goto){
  if(goto != ""){
    if($("#"+goto).length){
      $('html,body').animate({
        scrollTop: $("#"+goto).offset().top-40},
      'slow');
    }
  }
}


$(document).ready(function () {
  $('.dropdown-trigger').dropdown();
  $('.collapsible').collapsible();
  $('.tooltipped').tooltip();
  $('#modalShare').modal();
  $('#modalRequested').modal();
  $('#modalwr').modal();

  setTimeout(function() {
      goto = $("#goto").val();
      gotosection(goto);
    }, 1000);

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

  //Submit external link data to backend
  $("#requested-form").on("submit", function(event) {
      event.preventDefault();
      var elem = document.querySelectorAll('#modalRequested')[0];
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
              $('#requested-form')[0].reset();
              M.toast({html: data.message, classes: 'green rounded', displayLength:2000});
            }else{
              var elem = document.querySelectorAll('#modalRequested')[0];
              var instance = M.Modal.getInstance(elem);
              instance.open();
              M.toast({html: data.message, classes: 'red rounded', displayLength:10000});
            }
          },
          error:function(err) {
            var elem = document.querySelectorAll('#modalRequested')[0];
            var instance = M.Modal.getInstance(elem);
            instance.open();
            M.toast({html: gettext("Please check your inputs"), classes: 'red rounded', displayLength:10000});
          },
    });
  });

  /*$('.lang-item').each(function () {
    var $this = $(this);
    $this.on("click", function () {
        let code = $(this).data('code');
        $("#id_locale").val(code);
        $("#language-form").submit();
    });
  });*/

  $(".lang-item").click(function() {
    let code = $(this).data('code');
    $("#id_locale").val(code);
    $("#language-form").submit();
  });
  var elems = document.querySelectorAll('.collapsible.expandable');
  var instances = M.Collapsible.init(elems, {
    accordion: false
  });

  $(".se-pre-con").fadeOut("slow");
  $(".spinner-loading").fadeOut("slow");
  $(document).ajaxStart(function () {
      $(".se-pre-con").fadeIn("slow");
      $(".spinner-loading").fadeIn("slow");
  });

  $(document).ajaxComplete(function () {
      $(".se-pre-con").fadeOut("slow");
      $(".spinner-loading").fadeOut("slow");
  });
});

$(document).ready(function() {
  var btn = $('#backToTop');
  $(window).scroll(function() {
    if ($(window).scrollTop() > 100) {
      btn.removeClass('hide');
    } else {
      btn.addClass('hide');
    }
  });


  btn.on('click', function(e) {
    e.preventDefault();
    $('html, body').animate({scrollTop:0}, '300');
  });

  $(document).ready(function(){
    if($("#modalExternal").length){
      $('#modalExternal select').formSelect();
    }
    if($("#register").length){
      $('#register select').formSelect();
    }
    //$('.sidenav').sidenav();
    var elem = document.querySelector('#slide-out');
    var instance = M.Sidenav.init(elem, {
        edge:'left',
    });
  });

  $("#requested_country").on('change', function(e) {
     generate_states("requested_country", "requested_state");
  });
  $("#reqcountry").on('change', function(e) {
     generate_states("reqcountry", "reqstate");
  });
  $("#dtcountry").on('change', function(e) {
     generate_states("dtcountry", "dtstate");
  });
  $("#wrcountry").on('change', function(e) {
     generate_states("wrcountry", "wrstate");
  });
  $("#requested_title").keydown(function( event ) {
    if ( event.which == 13 ) {
     event.preventDefault();
    }
    generate_titles("requested_title",$("#requested_title").val(),"file");
  });
  $("#requested_title").bind("paste", function(e){
      value = e.originalEvent.clipboardData.getData('text');
      generate_titles("requested_title",value,"file", true);
  });
});
