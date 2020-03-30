//var loadedSchedule;
//var loadedUnits;


// function UpdateEstimateTime(schedulePath){
//     $.getJSON("api/get-time-estimate?schedulePath=" + schedulePath, function (result) {
//       console.log("estimate");
//       console.log(result);
//       totalLength = result['time'] * 3600;
//       console.log(totalLength);
//       $('#home-time').text(FormatTime(totalLength));
//       $('#home-time-summary').text(FormatTime(totalLength));
//     });
// }

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
});


//converts fahrenheit to celsius
function f2c(value){
  return (value - 32) * 5 / 9;
}



