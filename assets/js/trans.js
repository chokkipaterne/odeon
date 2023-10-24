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
//Show main menu
function mainmenu(){
  $(".mainmen").removeClass("hide");
  $(".subvizmenu").addClass("hide");
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



//handle share dash button
function share_dash(dash_code="", file_code=""){
  //$("#dash_code").val("");
  weblink = $("#weblink").val();
  $("#message").val(gettext("Hi, you might be interested in the following project: ")+weblink+'/'+dash_code);

  var elem = document.querySelectorAll('#modalShare')[0];
  var instance = M.Modal.getInstance(elem);
  instance.open();
}


//Handle share project or file button
function share_info(){
  //$("#dash_code").val("");
  weblink = $("#initweblink").val();
  webpath = $("#webpath").val();
  $("#message").val(gettext("Hi, you might be interested in the following content: ")+weblink+webpath);

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
//Hide or show menu of viz and dash
function moreopt(){
  $(".headdivtop").toggleClass("hide");
}


$(document).ready(function () {
  $('.dropdown-trigger').dropdown();
  $('.collapsible').collapsible();
  $('.tooltipped').tooltip();
  $('#modalShare').modal();

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


  $('.lang-item').each(function () {
    var $this = $(this);
    $this.on("click", function () {
        let code = $(this).data('code');
        $("#id_locale").val(code);
        $("#language-form").submit();
    });
  });
  var elems = document.querySelectorAll('.collapsible.expandable');
  var instances = M.Collapsible.init(elems, {
    accordion: false
  });

  $(".se-pre-con").fadeOut("slow");
  $(".spinner-loading").fadeOut("slow");
  $("#loader").fadeOut("slow");
  $(document).ajaxStart(function () {
      $(".se-pre-con").fadeIn("slow");
      $(".spinner-loading").fadeIn("slow");
      $("#loader").fadeIn("slow");
  });

  $(document).ajaxComplete(function () {
      $(".se-pre-con").fadeOut("slow");
      $(".spinner-loading").fadeOut("slow");
      $("#loader").fadeOut("slow");
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
});
