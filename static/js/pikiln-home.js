//Start Firing Schedule - inside pikiln-scripts.js
$('#btn-start-schedule').click(function () {
  $.getJSON("api/start-fire?schedulePath=" + loadedSchedule['path'], function (result) {
    console.log(result);
    $('#btn-start-schedule-modal').addClass('d-none');
    $('#btn-stop-schedule-modal').removeClass('d-none');
    $('#home-time-group').removeClass('d-none');
    $('#home-schedule-list').addClass('d-none');
    $('#home-estimates').addClass('d-none');
  });
});

//Stop Firing Schedule
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

//updates time left and progress bar on home page
function UpdateTimer(currentTime, totalTime){
  var percent = currentTime/totalTime;
  $('#home-time-bar').css("width", (percent * 100).toFixed(2) + '%');
  $('#home-time-remaining').text(FormatTime(totalTime - currentTime));
}