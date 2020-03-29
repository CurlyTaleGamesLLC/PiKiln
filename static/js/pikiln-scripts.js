var loadedSchedule;
var loadedUnits;

//loads drop down of options for firing schedules for both home page and edit firing schedules page
// function LoadSchedules() {
//   $.getJSON("api/list-schedules", function (result) {
//     console.log(result);
//     var dropdownHTML = '<option value="select-schedule" selected>Select Schedule</option>';

//     for (var i = 0; i < result['schedules'].length; i++) {
//       var optionValue = result['schedules'][i]['path'];
//       var optionName = result['schedules'][i]['name'];
//       var optionData = '<option value="' + optionValue + '">' + optionName + '</option>'
//       //console.log(optionName + " " + optionValue);
//       dropdownHTML += optionData;
//     }

//     $('#fireScheduleList').html(dropdownHTML);
//   });
// }

// //loads selected firing schedule for both home page and edit firing schedules page
// $('select[name="fireScheduleList"]').change(function () {
//   console.log("SELECT SCHEDULE");
//   if ($(this).val() != "select-schedule") {
//     console.log("Load " + $(this).val());
//     //editSchedule = $(this).val();

//     $.getJSON("api/get-schedule?schedulePath=" + $(this).val(), function (result) {
//       console.log(result);
//       console.log("schedule units = " + result['units']);
//       loadedSchedule = result;
//       loadedUnits = result['units'];
//       $('#schedule-title').text(result['name']);
//       if(result['units'] == "fahrenheit"){
//         $('.degrees').each(function () {$(this).html($(this).html().replace("°C", "°F"))});
//       }
//       else{
//         $('.degrees').each(function () {$(this).html($(this).html().replace("°F", "°C"))});
//       }
      
//       $('#schedule-body').html('');
//       for (i = 0; i < result['segments'].length; i++) {
//         var newRate = result['segments'][i]['rate'];
//         var newTemp = result['segments'][i]['temp'];
//         var newHold = result['segments'][i]['hold'];
//         var isEdit = window.location.pathname == "/firing-schedules";
//         var newSegment = LoadSegment(newRate, newTemp, newHold, isEdit);
//         $('#schedule-body').html($('#schedule-body').html() + newSegment);
//       }
//       $("#schedule-group").removeClass('d-none');
//     });

//     //Estimate Time
//     UpdateEstimateTime($(this).val());

//   }
// });


function UpdateEstimateTime(schedulePath){
    $.getJSON("api/get-time-estimate?schedulePath=" + schedulePath, function (result) {
      console.log("estimate");
      console.log(result);
      totalLength = result['time'] * 3600;
      console.log(totalLength);
      $('#home-time').text(FormatTime(totalLength));
      $('#home-time-summary').text(FormatTime(totalLength));
    });
}


function GetStatus() {
  $.getJSON("api/get-current-status", function (result) {
    console.log(result);

    //SetFiringButtons(result['status'] == "firing");

    if(result['status'] == "complete"){
      console.log("COMPLETE");
      //$('#home-time-summary').text();
      $('#home-cost-summary').text("$3.55");      
      //$('#home-complete').removeClass("d-none");
      //$('#time-cost-estimates').addClass("d-none");
    }
    else{
      //$('#home-complete').addClass("d-none");
    }

    if(result['status'] == "error"){
      console.log("ERROR");
      $('#home-error-title').text(" Faulty Relay #1");
      $('#home-error-message').text("The 1st relay is not properly turning off or on. Please turn off power and replace the faulty relay with a new one");
      //$('#home-error').removeClass("d-none");
      //$('#time-cost-estimates').addClass("d-none");
    }
     
    //$('#status-state').text(result['status']);
    //$('#status-start-time').text(result['start-time']);


  });

  //update time remaining
  // $.getJSON("api/get-total-time", function (result) {
  //   //console.log("time");
  //   console.log(result);
  //   UpdateTimer(result['currentTime'], result['totalTime']);
  // });
}

//highlight current page
function HighlightNav(){
  $('.nav-item').each(function () {
    //console.log($(this).attr('href'));
    if ("/" + $(this).attr('href') == window.location.pathname) {
      $(this).addClass("active");
    }
    if ($(this).attr('href') == "index" && window.location.pathname == "/") {
      $(this).addClass("active");
    }
  });
}

//only allow numbers to be entered into field with numbersOnly class
function NumbersOnly(){
  $('.numbersOnly').each(function () {

    var numberText = $(this).text();
    var regex = new RegExp(/[^0-9\.]/g); // expression here
    var isNumber = false;

    $(this).filter(function () {
      isNumber = regex.test(numberText);
      return isNumber;
    });

    if (isNumber) {
      console.log("DIFF " + numberText + " " + isNumber);
      $(this).text(numberText.replace(/[^0-9\.]/g, ''));
    }

    if (parseInt(numberText) > 9999) {
      $(this).text(9999)
    }
  });
}

//deselect input fields when enter is pressed
$(document).on('keypress',function(e) {
  if(e.which == 13) {
      $(':focus').blur()
  }
});

$(document).ready(function () {
  HighlightNav();

  //Filter Numbers Only
  setInterval(function () {NumbersOnly()}, 333);

  //GetStatus();
  //setInterval(function () { GetStatus() }, 5000);
  
});


//converts fahrenheit to celsius
function f2c(value){
  return (value - 32) * 5 / 9;
}

//format time to be hours:mins (2:45)
function FormatTime(value){
  valueMins = value / 60;
  if(valueMins < 0){
    valueMins = 0;
  }
  var hours = Math.floor(valueMins / 60).toString();
  var mins = Math.floor(valueMins % 60).toString();
  if(mins.length < 2){
    mins = "0" + mins;
  }
  return hours + ":" + mins;
}

