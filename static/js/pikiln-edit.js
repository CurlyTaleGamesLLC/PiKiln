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


$('#btn-add-segment').click(function () {
  const $clone = $TABLE.find('tbody tr').last().clone(true).removeClass('hide table-line');
  if ($TABLE.find('tbody tr').length === 0) {
    $('tbody').append(newTr);
  }
  $TABLE.find('table').append($clone);
});

function ScheduleToJSON(){
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
    //console.log($(this).html());
    //console.log(index % 6);

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

  //console.log(newSchedule);
  return newSchedule;
}

$('#btn-save-schedule').click(function () {
  console.log("Schedule Saved");

  $.ajax({
    type: "POST",
    contentType: "application/json; charset=utf-8",
    url: "api/save-schedule",
    data: JSON.stringify(ScheduleToJSON()),
    success: function (data) {
      console.log(data);
      LoadSchedules();

      //UpdateEstimateTime(data['path']);
      

      $('#alert-container').html('<div class="alert alert-warning alert-dismissible mt-1" role="alert" id="alert-save-settings"><strong>Schedule Saved!</strong><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');

      setTimeout(function () {
        $('#alert-container').html('')
      }, 4000);
    }
  });



});

$('#btn-delete-schedule').click(function () {
  console.log("Schedule Deleted");
  if (editSchedule == null) {return;}

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
    }
  });

});

$('#btn-create-schedule').click(function () {
  console.log("Schedule Created");
  $.post("api/create-schedule", function (data) {
    console.log(data);
    console.log(data['filename']);
    var newScheduleOption = '<option value="' + data['filename'] + '">' + 'Untitled Schedule' + '</option>'
    $('#fireScheduleList').html($('#fireScheduleList').html() + newScheduleOption);
    $("#fireScheduleList").val(data['filename']).change();
    //$("#schedule-group").removeClass('d-none');
  });
});

$('#btn-duplicate-schedule').click(function () {
  console.log("Schedule Duplicated");
  if (editSchedule == null) {return;}

  $.post("api/duplicate-schedule", {schedulePath: editSchedule}, function (data) {
    console.log(data);
    console.log(data['filename']);

    var newScheduleOption = '<option value="' + data['filename'] + '">' + data['name'] + '</option>'
    $('#fireScheduleList').html($('#fireScheduleList').html() + newScheduleOption);
    $("#fireScheduleList").val(data['filename']).change();
    //$("#schedule-group").removeClass('d-none');
  });
});

$('#btn-download-schedule').click(function () {
  console.log("Download Schedule");
  var selectedSchedule =  $('select[name="fireScheduleList"]').val();
  if (selectedSchedule != "select-schedule") {
    $.getJSON('api/get-schedule?schedulePath=' + selectedSchedule, function (result) {
      var json = JSON.stringify(result);
      var blob = new Blob([json], {type: "application/json"});
      var url  = URL.createObjectURL(blob);

      var link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', result['name'] + '.json');
      
      var aj = $(link);
      aj.appendTo('body');
      aj[0].click();
      aj.remove();
      
      URL.revokeObjectURL(url);
    });
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
  if ($row.index() === 0){return;}
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
     
  });
  return newHtml;
}

function AddTD(cellData){
  return '<td>' + cellData + '</td>';
}