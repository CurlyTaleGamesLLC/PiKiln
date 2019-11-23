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

$('#btn-add-segment').click( function() {
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
  newSchedule.path = editSchedule;
  newSchedule.segments = [];

  var index = 0;

  var saveRate;
  var saveTemp;
  var saveHold;

  $("td").each(function(){
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
      newSchedule.segments.push({rate: saveRate, temp: saveTemp, hold: saveHold});
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

$('#btn-delete-schedule').click( function() {
  console.log("Schedule Deleted");

  if(editSchedule == null){
    return;
  }

  $.ajax({
    url: 'api/delete-schedule?schedulePath=' + editSchedule,
    type: 'DELETE',
    success: function(result) {
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

$('#btn-create-schedule').click( function() {
  console.log("Schedule Created");
  $.post( "api/create-schedule", function( data ) {
    console.log(data);
    var newScheduleOption = '<option value="' + data + '">' + 'Untitled Schedule' + '</option>'
    $('#fireScheduleList').html($('#fireScheduleList').html() + newScheduleOption);
    $("#fireScheduleList").val(data).change();
    //$("#schedule-group").removeClass('d-none');
  });
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

 function LoadSettings(){
  $.getJSON("api/load-settings", function(result){
    console.log(result);
    $('#cost').val(result['cost']);
    $('#max-temp').val(result['max-temp']);

    $("#timezone").val(result['notifications']['timezone']);
     
    var units = (result['units'] == "celsius")
    console.log("units = " + units);
    
    if(units){
      $("#tempRadios2").removeAttr('checked');
      $("#tempRadios1").prop("checked", true);
    }
    else{
      $("#tempRadios1").removeAttr('checked');
      $("#tempRadios2").prop("checked", true);
    }

    var enableEmail = result['notifications']['enable-email'];
    if(enableEmail){
      $("#enable-email-off").removeAttr('checked');
      $("#enable-email-on").prop("checked", true);
    }
    else{
      $("#enable-email-on").removeAttr('checked');
      $("#enable-email-off").prop("checked", true);
    }
    
    

    $('#sender').prop('value', result['notifications']['sender']);
    $('#sender-password').prop('value', result['notifications']['sender-password']);
    $('#receiver').prop('value', result['notifications']['receiver']);
    
    //
  });
 }

 function LoadSchedules(){
  $.getJSON("api/list-schedules", function(result){
    console.log(result);

    var dropdownHTML = '<option value="select-schedule" selected>Select Schedule</option>';
    // 
    for(var i = 0; i < result['schedules'].length; i++){
      
      var optionValue = result['schedules'][i]['path'];
      var optionName = result['schedules'][i]['name'];
      var optionData = '<option value="' + optionValue + '">' + optionName + '</option>'
      
      console.log(optionName + " " + optionValue);
      dropdownHTML += optionData;
    }

    $('#fireScheduleList').html(dropdownHTML);
  });
 }

 $('#btn-save-settings').click( function() {
  $.post( './api/update-settings', $('form#form-settings').serialize(), function(data) {
       console.log("POSTED");
       console.log(data);
       //$('.alert').alert()
       $('#alert-container').html('<div class="alert alert-warning alert-dismissible mt-3" role="alert" id="alert-save-settings"><strong>Settings Saved!</strong><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
     },
     'json' // I expect a JSON response
  );
});

$('select[name="fireScheduleList"]').change(function(){
  if($(this).val() != "select-schedule"){
    console.log("Load " + $(this).val());
    editSchedule = $(this).val();

    //$("#fireScheduleList option[value='select-schedule']").remove();
    $.getJSON("api/get-schedule?schedulePath=" + $(this).val(), function(result){
      console.log(result);
      $('#schedule-title').text(result['name']);
      $('#schedule-body').html('');
      for(i = 0; i < result['segments'].length; i++){
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




function SetCurrentPage(){
  //active
  
}

function LoadSegment(rate, temp, hold, isEdit){
  var html = '<tr class="segment-row"><td></td><td class="numbersOnly" contenteditable="' + isEdit + '">';
  html += rate;
  html += '</td><td class="numbersOnly" contenteditable="' + isEdit + '">';
  html += temp;
  html += '</td><td class="numbersOnly" contenteditable="' + isEdit + '">'
  html += hold;
  html += '</td>'
  if(isEdit){
    html += '<td class="pt-3-half"><span class="table-up mr-2"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-up" aria-hidden="true"></i></a></span><span class="table-down"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-down" aria-hidden="true"></i></a></span></td><td><span class="table-remove"><button type="button" class="btn btn-danger btn-rounded btn-sm my-0"><i class="fas fa-trash"></i></button></span></td></tr>';
  }
  
  return html;
}


//Filter Numbers Only
$(document).ready(function () {

  GetSettings();

  //highlight current page
  $('.nav-item').each(function(){
    console.log($(this).attr('href'));
    if("/" + $(this).attr('href') == window.location.pathname){
      $(this).addClass("active");
    }
    if($(this).attr('href') == "index" && window.location.pathname == "/"){
      $(this).addClass("active");
    }
  });

  setInterval(function() {
    $('.numbersOnly').each(function(){
      var regex = new RegExp(/[^0-9\.]/g); // expression here
      var isNumber = false;

      $(this).filter(function () {
        isNumber = regex.test($(this).text());
        //console.log("TEST " + $(this).text() + " " + text);
        return isNumber;
      });

      if (isNumber) {
        console.log("DIFF " + $(this).text() + " " + isNumber);
        $(this).text($(this).text().replace(/[^0-9\.]/g, ''));
      }

      if(parseInt($(this).text()) > 9999){
        $(this).text(9999)
      }
    });
  }, 333);
});

function GetSettings(){
  $.getJSON("api/load-settings", function(result){
    console.log(result);
    //$('#cost').val(result['cost']);
    //$('#max-temp').val(result['max-temp']);
    var units = (result['units'] == "celsius")
    console.log("units = " + units);

    //swaps degrees to F
    if(!units){
      $('.degrees').each(function(){
        $(this).html($(this).html().replace("°C", "°F"));
      });
    }
   
  });
}