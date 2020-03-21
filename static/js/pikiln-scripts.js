var loadedSchedule;
var loadedUnits;

//loads drop down of options for firing schedules for both home page and edit firing schedules page
function LoadSchedules() {
  $.getJSON("api/list-schedules", function (result) {
    console.log(result);
    var dropdownHTML = '<option value="select-schedule" selected>Select Schedule</option>';

    for (var i = 0; i < result['schedules'].length; i++) {
      var optionValue = result['schedules'][i]['path'];
      var optionName = result['schedules'][i]['name'];
      var optionData = '<option value="' + optionValue + '">' + optionName + '</option>'
      //console.log(optionName + " " + optionValue);
      dropdownHTML += optionData;
    }

    $('#fireScheduleList').html(dropdownHTML);
  });
}

//loads selected firing schedule for both home page and edit firing schedules page
$('select[name="fireScheduleList"]').change(function () {
  if ($(this).val() != "select-schedule") {
    console.log("Load " + $(this).val());
    editSchedule = $(this).val();

    $.getJSON("api/get-schedule?schedulePath=" + $(this).val(), function (result) {
      console.log(result);
      console.log("schedule units = " + result['units']);
      loadedSchedule = result;
      loadedUnits = result['units'];
      $('#schedule-title').text(result['name']);
      if(result['units'] == "fahrenheit"){
        $('.degrees').each(function () {$(this).html($(this).html().replace("°C", "°F"))});
      }
      else{
        $('.degrees').each(function () {$(this).html($(this).html().replace("°F", "°C"))});
      }
      
      $('#schedule-body').html('');
      for (i = 0; i < result['segments'].length; i++) {
        var newRate = result['segments'][i]['rate'];
        var newTemp = result['segments'][i]['temp'];
        var newHold = result['segments'][i]['hold'];
        var isEdit = window.location.pathname == "/firing-schedules";
        var newSegment = LoadSegment(newRate, newTemp, newHold, isEdit);
        $('#schedule-body').html($('#schedule-body').html() + newSegment);
      }
      $("#schedule-group").removeClass('d-none');

      //Estimate Time
      UpdateEstimateTime();
    });
  }
});


//constantly re-calculates the estimated firing time on the edit firing schedule page
function UpdateEstimateTime(){
  console.log("update time estimate");
  if(loadedSchedule == null){
    return;
  }
  console.log("update time estimate2");
  if(window.location.pathname == "/firing-schedules"){
    loadedSchedule = ScheduleToJSON();
  }
  console.log(loadedSchedule);
  var totalLength = 0;

  //assume room temperature
  var startTemp = loadedUnits == "fahrenheit" ? 72 : 22.222;
  startTemp = 0;

  for(var i = 0; i < loadedSchedule['segments'].length; i++){
    var tempDifference = Math.abs(loadedSchedule['segments'][i]['temp'] - startTemp)
    var rampTime = (tempDifference/loadedSchedule['segments'][i]['rate']) * 60;
    //console.log("seg + " + rampTime);
		totalLength += rampTime * 60;
		//console.log("hold + " + loadedSchedule['segments'][i]['hold']);
    totalLength += loadedSchedule['segments'][i]['hold'];
    startTemp = loadedSchedule['segments'][i]['temp'];
  }
  //console.log("totalLength = " + totalLength);

  $('#home-time').text(FormatTime(totalLength));
  $('#home-time-summary').text(FormatTime(totalLength));
  return totalLength
}

//create html for a row in a firing schedule
function LoadSegment(rate, temp, hold, isEdit) {
  var html = '<tr class="segment-row"><td></td><td class="numbersOnly" contenteditable="' + isEdit + '">';
  html += rate;
  html += '</td><td class="numbersOnly" contenteditable="' + isEdit + '">';
  html += temp;
  html += '</td><td class="numbersOnly" contenteditable="' + isEdit + '">'
  html += hold;
  html += '</td>'
  if (isEdit) {
    html += '<td class="pt-3-half"><span class="table-up mr-2"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-up" aria-hidden="true"></i></a></span><span class="table-down"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-down" aria-hidden="true"></i></a></span></td><td><span class="table-remove"><button type="button" class="btn btn-danger btn-rounded btn-sm my-0"><i class="fas fa-trash"></i></button></span></td></tr>';
  }

  return html;
}

function GetStatus() {
  $.getJSON("api/get-current-status", function (result) {
    console.log(result);

    //display the name of the firing schedule in the nav bar
    if(result['status'] == "firing"){
      $.getJSON("api/get-current-schedule", function (result2) {
        $('.current-schedule').each(function () {$(this).text(" | " + result2['name'])});
      });
    }
    else{
      $('.current-schedule').each(function () {$(this).text("")});
    }

    if(result['status'] == "complete"){
      console.log("COMPLETE");
      //$('#home-time-summary').text();
      $('#home-cost-summary').text("$3.55");      
      $('#home-complete').removeClass("d-none");
      $('#time-cost-estimates').addClass("d-none");
    }
    else if(result['status'] == "error"){
      console.log("ERROR");
      $('#home-error-title').text(" Faulty Relay #1");
      $('#home-error-message').text("The 1st relay is not properly turning off or on. Please turn off power and replace the faulty relay with a new one");
      $('#home-error').removeClass("d-none");
      $('#time-cost-estimates').addClass("d-none");
    }
     
    //$('#status-state').text(result['status']);
    //$('#status-start-time').text(result['start-time']);

    //update currently selected segment on the home page
    if (window.location.pathname == "/" || window.location.pathname == "/index") {
      $.getJSON("api/get-current-segment", function (result2) {
        console.log(result2)
        $('.segment-row').each(function () {
          var isFiring = result['status'] == "firing"
          var isSegmentIndex = $(this).index() == result2['segment']
          if (isFiring && isSegmentIndex) {
            $(this).addClass("current-segment");
            $(this).addClass("text-light");
          }
          else {
            $(this).removeClass("current-segment");
            $(this).removeClass("text-light");
          }
        });
      });
    }

  });

   //update the current temperature inside the kiln in the nav bar
   $.getJSON("api/temperature", function (result) {
     //need to pass units as well with temp
     console.log(result);
    var tempUnits = result['units'] == "celsius" ? "°C" : "°F";
    var tempUnitsText = result['temp'] + tempUnits;
    $('.current-temperature').each(function () {$(this).text(tempUnitsText)});
  });

  //update time remaining
  $.getJSON("api/get-total-time", function (result) {
    console.log("time");
    console.log(result);
    UpdateTimer(result['currentTime'], result['totalTime']);
    //UpdateTimer(result['totalTime']/2, result['totalTime']);
  });
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

  GetStatus();
  setInterval(function () { GetStatus() }, 5000);
  
  if(window.location.pathname == "/firing-schedules"){
    setInterval(function () {UpdateEstimateTime()}, 333);
  }
  
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