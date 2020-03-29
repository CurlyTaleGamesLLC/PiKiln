// var app = new Vue({
//   el: '#app',
//   data: {
//     settings:[]
//   },
//   delimiters: ['[[', ']]'],
//   methods: {
//       loadSettings: function () {
//           var self = this;
//           axios.get("/api/load-settings").then(response => {
//               self.settings = response.data;
//               console.log("settings:");
//               console.log(self.settings);
//           });
//       },

//       saveSettings: function () {
//           var self = this;

//           //validate email
//           var reg = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$/
//           self.settings.email = reg.test(self.settings.email) ? self.settings.email : "";

//           axios.post('/api/save-settings', self.settings)
//               .then(response => {
//                   console.log(response.data);
//                   $('#alert-container').html('<div class="alert alert-warning alert-dismissible mt-3" role="alert" id="alert-save-settings"><strong>Settings Saved!</strong><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');

//                   setTimeout(function () {
//                     $('#alert-container').html('')
//                   }, 4000);
//               });
//       }
//   },
//   mounted: function () {
//       this.loadSettings();
//       //axios.get("http://localhost:5000/test").then(response => (console.log(response)))
//   }
// })