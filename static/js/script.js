const $TABLE = $('#table');
const $BTN = $('#export-btn');
const $EXPORT = $('#export');

var editSchedule;

const newTr = `
<tr class="segment-row hide">
    <td></td>
    <td class="numbersOnly" contenteditable="true">50</td>
    <td class="numbersOnly" contenteditable="true">1000</td>
    <td class="numbersOnly" contenteditable="true">50</td>
    <td class="pt-3-half">
    <span class="table-up mr-2"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-up" aria-hidden="true"></i></a></span>
    <span class="table-down"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-down" aria-hidden="true"></i></a></span>
    </td>
    <td>
    <span class="table-remove"><button type="button" class="btn btn-danger btn-rounded btn-sm my-0"><i class="fas fa-trash"></i></button></span>
    </td>
</tr>`;

$('#btn-start-schedule').click(function () {
  $.getJSON("api/start-fire", function (result) {
    console.log(result);
    $('#btn-start-schedule-modal').addClass('d-none');
    $('#btn-stop-schedule-modal').removeClass('d-none');
    $('#home-time-group').removeClass('d-none');
    $('#home-schedule-list').addClass('d-none');
    $('#home-estimates').addClass('d-none');
  });
});

$('#btn-stop-schedule').click(function () {
  $.getJSON("api/stop-fire", function (result) {
    console.log(result);
    $('#btn-stop-schedule-modal').addClass('d-none');
    $('#btn-start-schedule-modal').removeClass('d-none');
    $('#home-time-group').addClass('d-none');
    $('#home-schedule-list').removeClass('d-none');
    $('#home-estimates').removeClass('d-none');
  });
});

function UpdateTimer(currentTime, totalTime){
  var percent = currentTime/totalTime;
  $('#home-time-bar').css("width", (percent * 100).toFixed(2) + '%');

  $('#home-time-remaining').text(FormatTime(totalTime - currentTime));
}


$('#btn-add-segment').click(function () {
  const $clone = $TABLE.find('tbody tr').last().clone(true).removeClass('hide table-line');

  if ($TABLE.find('tbody tr').length === 0) {

    $('tbody').append(newTr);
  }

  $TABLE.find('table').append($clone);
});

$('#btn-save-schedule').click(function () {
  console.log("Schedule Saved");

  var newSchedule = new Object();
  newSchedule.name = $('#schedule-title').text();
  newSchedule.units = loadedUnits;
  newSchedule.path = editSchedule;
  newSchedule.segments = [];

  var index = 0;

  var saveRate;
  var saveTemp;
  var saveHold;

  $(".segment-row td").each(function () {
    console.log($(this).html());
    console.log(index % 6);

    if (index % 6 == 1) {
      saveRate = parseInt($(this).text());
    }
    if (index % 6 == 2) {
      saveTemp = parseInt($(this).text());
    }
    if (index % 6 == 3) {
      saveHold = parseInt($(this).text());
      newSchedule.segments.push({ rate: saveRate, temp: saveTemp, hold: saveHold });
    }
    index++;
  });

  console.log(newSchedule);


  $.ajax({
    type: "POST",
    contentType: "application/json; charset=utf-8",
    url: "api/save-schedule",
    data: JSON.stringify(newSchedule),
    success: function (data) {
      console.log(data);
      LoadSchedules();

      $('#alert-container').html('<div class="alert alert-warning alert-dismissible mt-1" role="alert" id="alert-save-settings"><strong>Schedule Saved!</strong><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');

      setTimeout(function () {
        $('#alert-container').html('')
      }, 4000);
    }
  });



});

$('#btn-delete-schedule').click(function () {
  console.log("Schedule Deleted");

  if (editSchedule == null) {
    return;
  }

  $.ajax({
    url: 'api/delete-schedule?schedulePath=' + editSchedule,
    type: 'DELETE',
    success: function (result) {
      console.log(result);
      $("#fireScheduleList").val("select-schedule").change();
      $("#fireScheduleList option[value='" + editSchedule + "']").remove();
      $('#schedule-title').text('');
      $('#schedule-body').html('');
      $("#schedule-group").addClass('d-none');

      editSchedule = null;

      // Do something with the result
    }
  });

});

$('#btn-create-schedule').click(function () {
  console.log("Schedule Created");
  $.post("api/create-schedule", function (data) {
    console.log(data);
    var newScheduleOption = '<option value="' + data + '">' + 'Untitled Schedule' + '</option>'
    $('#fireScheduleList').html($('#fireScheduleList').html() + newScheduleOption);
    $("#fireScheduleList").val(data).change();
    //$("#schedule-group").removeClass('d-none');
  });
});

$('#btn-download-schedule').click(function () {
  console.log("Download Schedule");
  var selectedSchedule =  $('select[name="fireScheduleList"]').val();
  if (selectedSchedule != "select-schedule") {
    window.open('api/get-schedule?schedulePath=' + selectedSchedule);    
  }
});

$('#btn-import-schedule').click(function () {
  console.log("Import Schedule");
  $('#import-schedule').click();
});

//auto submits the schedule import upload
$('#import-schedule').on('change', function () {
  $('#importForm').submit();
});


$TABLE.on('click', '.table-remove', function () {

  $(this).parents('tr').detach();
});

$TABLE.on('click', '.table-up', function () {

  const $row = $(this).parents('tr');

  if ($row.index() === 0) {
    return;
  }

  $row.prev().before($row.get(0));
});

$TABLE.on('click', '.table-down', function () {

  const $row = $(this).parents('tr');
  $row.next().after($row.get(0));
});

// A few jQuery helpers for exporting only
jQuery.fn.pop = [].pop;
jQuery.fn.shift = [].shift;

$BTN.on('click', () => {

  const $rows = $TABLE.find('tr:not(:hidden)');
  const headers = [];
  const data = [];

  // Get the headers (add special header logic here)
  $($rows.shift()).find('th:not(:empty)').each(function () {

    headers.push($(this).text().toLowerCase());
  });

  // Turn all existing rows into a loopable array
  $rows.each(function () {
    const $td = $(this).find('td');
    const h = {};

    // Use the headers from earlier to name our hash keys
    headers.forEach((header, i) => {

      h[header] = $td.eq(i).text();
    });

    data.push(h);
  });

  // Output the result
  $EXPORT.text(JSON.stringify(data));
});

//  function ReIndexSegments(){
//     $TABLE.find('table')
//  }

function LoadSettings() {
  $.getJSON("api/load-settings", function (result) {
    console.log(result);
    $('#cost').val(result['cost']);
    $('#max-temp').val(result['max-temp']);
    $('#volts').val(result['volts']);
    $("#timezone").val(result['notifications']['timezone']);

    var units = (result['units'] == "celsius")
    console.log("units = " + units);

    if (units) {
      $("#tempRadios2").removeAttr('checked');
      $("#tempRadios1").prop("checked", true);
    }
    else {
      $("#tempRadios1").removeAttr('checked');
      $("#tempRadios2").prop("checked", true);
    }

    var enableEmail = result['notifications']['enable-email'];
    if (enableEmail) {
      $("#enable-email-off").removeAttr('checked');
      $("#enable-email-on").prop("checked", true);
    }
    else {
      $("#enable-email-on").removeAttr('checked');
      $("#enable-email-off").prop("checked", true);
    }

    $('#sender').prop('value', result['notifications']['sender']);
    $('#sender-password').prop('value', result['notifications']['sender-password']);
    $('#receiver').prop('value', result['notifications']['receiver']);
  });
}

function LoadSchedules() {
  $.getJSON("api/list-schedules", function (result) {
    console.log(result);
    var dropdownHTML = '<option value="select-schedule" selected>Select Schedule</option>';

    for (var i = 0; i < result['schedules'].length; i++) {
      var optionValue = result['schedules'][i]['path'];
      var optionName = result['schedules'][i]['name'];
      var optionData = '<option value="' + optionValue + '">' + optionName + '</option>'
      console.log(optionName + " " + optionValue);
      dropdownHTML += optionData;
    }

    $('#fireScheduleList').html(dropdownHTML);
  });
}

$('#btn-save-settings').click(function () {
  $.post('./api/update-settings', $('form#form-settings').serialize(), function (data) {
    console.log("POSTED");
    console.log(data);
    //$('.alert').alert()
    $('#alert-container').html('<div class="alert alert-warning alert-dismissible mt-3" role="alert" id="alert-save-settings"><strong>Settings Saved!</strong><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
  },
    'json' // I expect a JSON response
  );
});

var loadedUnits;
$('select[name="fireScheduleList"]').change(function () {
  if ($(this).val() != "select-schedule") {
    console.log("Load " + $(this).val());
    editSchedule = $(this).val();

    //$("#fireScheduleList option[value='select-schedule']").remove();
    $.getJSON("api/get-schedule?schedulePath=" + $(this).val(), function (result) {
      console.log(result);
      console.log("schedule units = " + result['units']);
      
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

    });

  }
});

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




var currentUnits;
function GetSettings() {
  $.getJSON("api/load-settings", function (result) {
    console.log(result);
    //$('#cost').val(result['cost']);
    //$('#max-temp').val(result['max-temp']);
    var units = (result['units'] == "celsius")
    console.log("units = " + units);
    currentUnits = result['units'];
  });
}

function GetStatus() {
  $.getJSON("api/load-status", function (result) {
    console.log(result);
    $('#status-schedule').text(result['name']);
    $('#status-state').text(result['status']);
    $('#status-start-time').text(result['start-time']);

    $.getJSON("api/temperature", function (result2) {
      var tempUnits = result['units'] == "celsius" ? "°C" : "°F";
      var tempUnitsText = result2['temp'] + tempUnits;
      $('#home-current-temperature').text(tempUnitsText);
      $('#status-temp').text(tempUnitsText);
    });

    $.getJSON("api/get-current-segment", function (result3) {
      console.log(result3)
      $('.segment-row').each(function () {
        var isFiring = result['status'] == "firing"
        // console.log("checking segment index");
        // console.log($(this).index());
        // console.log(result3['segment']);
        // console.log(result['status']);
        // console.log(result['status'] == "firing");
        var isSegmentIndex = $(this).index() == result3['segment']
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

  });
  $.getJSON("api/get-total-time", function (result) {
    UpdateTimer(result['current-time'], result['total-time']);
  });
}

function HighlightNav(){
  //highlight current page
  $('.nav-item').each(function () {
    console.log($(this).attr('href'));
    if ("/" + $(this).attr('href') == window.location.pathname) {
      $(this).addClass("active");
    }
    if ($(this).attr('href') == "index" && window.location.pathname == "/") {
      $(this).addClass("active");
    }
  });
}

function NumbersOnly(){
  $('.numbersOnly').each(function () {

    var numberText = $(this).text();

    var regex = new RegExp(/[^0-9\.]/g); // expression here
    var isNumber = false;

    $(this).filter(function () {
      isNumber = regex.test(numberText);
      //console.log("TEST " + $(this).text() + " " + text);
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

$(document).ready(function () {
  HighlightNav();

  //Filter Numbers Only
  setInterval(function () {NumbersOnly()}, 333);

  GetStatus();
  setInterval(function () { GetStatus() }, 5000); 
});

function CelsiusConeChart(){
  console.log("rows?");
  var index = 0;

  $('.cone-row').each(function() {
    if(index > 0){
      var newHtml = $(this).html();

      var newTemp = $(this).find("td").eq(3).text().replace("°F", "");
      newTemp = f2c(parseInt(newTemp));

      newHtml += AddTD(newTemp.toFixed(0) + "°C");
      console.log(newHtml);
      
      $(this).html(newHtml);
    }
    index++;
  });
}

function f2c(value){
  return (value - 32) * 5 / 9;
}

//format time to be hours:mins (2:45)
function FormatTime(value){
  var hours = Math.floor(value / 60).toString();
  var mins = Math.floor(value % 60).toString();
  if(mins.length < 2){
    mins = "0" + mins;
  }
  return hours + ":" + mins;
}



function GetTotals(){
  $.getJSON("api/load-totals", function (result) {
    console.log(result);

    $('#log-fires').text(result['fires']);
    
    //format time to be hours:mins (2:45)
    // var hours = Math.floor(result['time'] / 60).toString();
    // var mins = Math.floor(result['time'] % 60).toString();
    // if(mins.length < 2){
    //   mins = "0" + mins;
    // }
    $('#log-time').text(FormatTime(result['time']));

    var formatCost = "$";
    if(result['cost'] < 1){
      formatCost += "0.";
    }
    if(result['cost'] < .10){
      formatCost += "0";
    }
    formatCost += result['cost'].toString();

    $('#log-cost').text(formatCost);

  });
}

function ScrapeTable(){
  var newHtml = "";
  var index = 0;
  $('#cone-table tr').each(function() {
    
    if(index < 36){
      newHtml += '<tr>'; 
      newHtml += AddTD($(this).find("td").eq(0).text());
      newHtml += AddTD($(this).find("td").eq(1).text());
      newHtml += AddTD($(this).find("td").eq(2).text());
      newHtml += AddTD($(this).find("td").eq(3).text());
      index++;
      newHtml += '</tr>';
    }
    
    //var customerId = $(this).find("td").eq(2).html();    
  });
  return newHtml;
}

function AddTD(cellData){
  return '<td>' + cellData + '</td>';
}