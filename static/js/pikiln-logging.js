function GetTotals(){
  $.getJSON("api/load-totals", function (result) {
    console.log(result);

    $('#log-fires').text(result['fires']);
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