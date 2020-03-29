//Start Firing Schedule - inside pikiln-scripts.js
$('#btn-start-schedule').click(function () {
  $.getJSON("api/start-fire?schedulePath=" + loadedSchedule['path'], function (result) {
    console.log("Start Firing");
    console.log(result);
    //$('#btn-start-schedule-modal').addClass('d-none');
    //$('#btn-stop-schedule-modal').removeClass('d-none');
    
    $('#home-schedule-list').addClass('d-none');
    //$('#home-estimates').addClass('d-none');
    //SetFiringButtons(true);
    //GetStatus();
  });
});

//Stop Firing Schedule
$('#btn-stop-schedule').click(function () {
  $.getJSON("api/stop-fire", function (result) {
    console.log(result);
    console.log("Stop Firing");
    //$('#btn-stop-schedule-modal').addClass('d-none');
    //$('#btn-start-schedule-modal').removeClass('d-none');
   
    $('#home-schedule-list').removeClass('d-none');
    //$('#home-estimates').removeClass('d-none');
    //SetFiringButtons(false);
    GetStatus();
  });
});

//updates time left and progress bar on home page
// function UpdateTimer(currentTime, totalTime){
//   var percent = currentTime/totalTime;
//   $('#home-time-bar').css("width", (percent * 100).toFixed(2) + '%');
//   $('#home-time-remaining').text(FormatTime(totalTime - currentTime));
// }