var app = new Vue({
    el: '#app',
    data: {
      firing:{
        status:'firing',
        name:'test firing',
        segment:0
      },
      schedule:{
          name:'test',
          path:'2d90d327-f107-4c9f-8c4a-d785cc227cc7.json',
          segments:[
            {
                hold:60,
                rate:100,
                temp:500
            },
            {
                hold:60,
                rate:9999,
                temp:2167
            },
            {
                hold:60,
                rate:120,
                temp:800
            }
        ],
        units:"fahrenheit"
    },
    scheduleList:[
        {
            name:'test1',
            path:'123.json'
        },
        {
            name:'test2',
            path:'1234.json'
        },
        {
            name:'test3',
            path:'12345.json'
        }
    ],
      cTemp:[],
      settings:[]
    },
    delimiters: ['[[', ']]'],
    methods: {
      //loads the settings
      loadSettings: function () {
          var self = this;
          axios.get("/api/load-settings").then(response => {
              self.settings = response.data;
              console.log("settings:");
              console.log(self.settings);
          });
      },
  
      //saves the settings, and checks to make sure the email address is valid
      saveSettings: function () {
          var self = this;
  
          //validate email address format
          var reg = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$/
          self.settings.email = reg.test(self.settings.email) ? self.settings.email : "";
  
          axios.post('/api/save-settings', self.settings)
              .then(response => {
                  console.log(response.data);
                  $('#alert-container').html('<div class="alert alert-warning alert-dismissible mt-3" role="alert" id="alert-save-settings"><strong>Settings Saved!</strong><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
  
                  setTimeout(function () {
                    $('#alert-container').html('')
                  }, 4000);
              });
      },
  
      //updates the current temperature in the navigation bar and on the home screen during a fire
      getCurrentTemp: function(){
        var self = this;
        axios.get("/api/temperature").then(response => {
          self.cTemp = response.data;
        });
      },

      //updates the highlighted segment when a schedule is being fired
      getCurrentSegment: function(){
        var self = this;
        axios.get("/api/get-current-segment").then(response => {
          self.firing = response.data;
          $('#home-time-remaining').text(FormatTime(self.firing.totalTime - self.firing.currentTime));
        });
      },

      //gets list of all firing schedules
      getScheduleList: function(){
        var self = this;
        axios.get("/api/list-schedules").then(response => {
          self.scheduleList = response.data;
        });
      },

      //load schedule selected from dropdown
      onScheduleSelect: function(event){
        if (event.target.value != "select-schedule") {
            var self = this;
            axios.get("/api/get-schedule?schedulePath=" + event.target.value).then(response => {
                self.schedule = response.data;
                //UpdateEstimateTime($(this).val());
            });
        }
      }

      //$.getJSON("api/get-schedule?schedulePath=" + $(this).val(), function (result) {
      
  },
    mounted: function () {
      if (window.location.pathname == "/" || window.location.pathname == "/index") {
        //home page
        this.getScheduleList();
      }
      if (window.location.pathname == "/settings") {
        this.loadSettings();
      }
  
      //continually gets the current temperature
      this.getCurrentTemp();
      setInterval(() => {this.getCurrentTemp()}, 3000);

      //continually gets the current status
      this.getCurrentSegment();
      setInterval(() => {this.getCurrentSegment()}, 5000);
      
    }
  });




  //loads selected firing schedule for both home page and edit firing schedules page
$('select[name="fireScheduleListzz"]').change(function () {
    console.log("SELECT SCHEDULE");
    if ($(this).val() != "select-schedule") {
      console.log("Load " + $(this).val());
      //editSchedule = $(this).val();
  
      $.getJSON("api/get-schedule?schedulePath=" + $(this).val(), function (result) {
        console.log(result);
        console.log("schedule units = " + result['units']);
        //loadedSchedule = result;
        //loadedUnits = result['units'];
        //$('#schedule-title').text(result['name']);
        
        
        // $('#schedule-body').html('');
        // for (i = 0; i < result['segments'].length; i++) {
        //   var newRate = result['segments'][i]['rate'];
        //   var newTemp = result['segments'][i]['temp'];
        //   var newHold = result['segments'][i]['hold'];
        //   var isEdit = window.location.pathname == "/firing-schedules";
        //   var newSegment = LoadSegment(newRate, newTemp, newHold, isEdit);
        //   $('#schedule-body').html($('#schedule-body').html() + newSegment);
        // }
        // $("#schedule-group").removeClass('d-none');
      });
  
      //Estimate Time
      UpdateEstimateTime($(this).val());
  
    }
  });


//   function LoadSegment(rate, temp, hold, isEdit) {
//     var html = '<tr :class="{"segment-row" : true, "current-segment" : $(this).index() == firing.segment, "text-light" : $(this).index() == firing.segment}"><td></td><td class="numbersOnly" contenteditable="' + isEdit + '">';
//     html += rate;
//     html += '</td><td class="numbersOnly" contenteditable="' + isEdit + '">';
//     html += temp;
//     html += '</td><td class="numbersOnly" contenteditable="' + isEdit + '">'
//     html += hold;
//     html += '</td>'
//     if (isEdit) {
//       html += '<td class="pt-3-half"><span class="table-up mr-2"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-up" aria-hidden="true"></i></a></span><span class="table-down"><a class="badge badge-secondary" href="#!"><i class="fas fa-long-arrow-alt-down" aria-hidden="true"></i></a></span></td><td><span class="table-remove"><button type="button" class="btn btn-danger btn-rounded btn-sm my-0"><i class="fas fa-trash"></i></button></span></td></tr>';
//     }
  
//     return html;
//   }


  
