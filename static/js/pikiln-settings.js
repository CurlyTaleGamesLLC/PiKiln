//loads data for settings page
function LoadSettings() {
  $.getJSON("api/load-settings", function (result) {
    console.log(result);
    $('#cost').val(result['cost']);
    $('#max-temp').val(result['max-temp']);
    $('#offset-temp').val(result['offset-temp']);
    $('#volts').val(result['volts']);
    $("#timezone").val(result['notifications']['timezone']);

    var units = (result['units'] == "celsius")
    console.log("units = " + units);

    $('#units-setting').bootstrapToggle(units ? "off" : "on");

    var enableEmail = result['notifications']['enable-email'];
    $('#toggle-email').bootstrapToggle(enableEmail ? "on" : "off");
    

    $('#sender').prop('value', result['notifications']['sender']);
    $('#sender-password').prop('value', result['notifications']['sender-password']);
    $('#receiver').prop('value', result['notifications']['receiver']);
  });
}


//submits form and saves settings data
$('#btn-save-settings').click(function () {
  $.post('./api/update-settings', $('form#form-settings').serialize(), function (data) {
    console.log("POSTED");
    console.log(data);
    //$('.alert').alert()
    $('#alert-container').html('<div class="alert alert-warning alert-dismissible mt-3" role="alert" id="alert-save-settings"><strong>Settings Saved!</strong><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');

    setTimeout(function () {
      $('#alert-container').html('')
    }, 4000);
    
  },
    'json' // I expect a JSON response
  );
});


//i don't think this is being used
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