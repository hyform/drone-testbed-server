$(document).ready(function () {
    var ajaxUrl = getAjaxUrl("exper");

    function getId(thiss) {
        thisId = $(thiss).attr('id');
        idSplit = thisId.split("_");
        idSplitId = idSplit[idSplit.length - 1];
        return idSplitId;
    }

    $('#return_from_digital_twin').on('click', function () {
      window.location.href = "/experiment";
    })

    $('#update_digital_twin').on('click', function () {

      var dict = {};
      inputs = document.getElementsByTagName('input');
      for (index = 0; index < inputs.length; ++index) {
        if (inputs[index].name != undefined && inputs[index].name != ""){
          // deal with inputs[index] element.
          var tokens = inputs[index].name.split("-")
          var var_name = tokens[0]
          var id = tokens[1]
          var input_value = inputs[index].value
          var result = dict[id] === undefined
          if (result){
            dict[id] = {}
          }
          dict[id][var_name] = input_value
        }
      }

      for(var key in dict) {
          var item_str = JSON.stringify(dict[key]);
          createAjaxUrl = ajaxUrl + "digital_twin/" + key + "/"
          $.ajax({
              url: createAjaxUrl,
              method: "PUT",
              data: {
                open_time_interval : dict[key]['open_time_interval'],
                save_time_interval : dict[key]['save_time_interval'],
                quality_bias : dict[key]['quality_bias'],
                self_bias : dict[key]['self_bias'],
                temperature : dict[key]['temperature'],
                satisficing_factor : dict[key]['satisficing_factor']
              },
              error: function (result) {
                  //TODO: error message
                  alert("New digital twin configuration failed to save");
              },
              success: function (result) {
                  //clear new sessions
                  console.log("configuration saved");
              }
          });

      }

      window.location.href = "/experiment";


        //var newSessions = document.querySelectorAll('.new-session');
        //var numNewSessions = newSessions.length;
        //if(numNewSessions < 1) {
        //    alert("Please create at least one new session");
        //    return;
        //}

        //sessionNameNew = $("#session-name-new").val();
        //if(sessionNameNew) {
        //    var keepGoing = confirm("A new session may have not been added via the + button.\nContinue anyway?");
        //    if(!keepGoing) {
        //        return;
        //    }
        //}

        //teamId = $("#select-session-team option:selected").val();

        //var newSessionList = [];
        //for (i = 0; i < newSessions.length; ++i) {
        //    newSessionList.push(new Object());
        //};

        //var newSessionNames = document.querySelectorAll('.new-session-name');
        //for (i = 0; i < newSessionNames.length; ++i) {
        //    let name = newSessionNames[i].value;
        //    if(name) {
        //        newSessionList[i].name = name;
        //    } else {
        //        let index = i + 1;
        //        alert("New session " + index + " does not have a name");
        //        return;
        //    }
        //}

        //var newSessionAI = document.querySelectorAll('.new-session-ai');
        //for (i = 0; i < newSessionAI.length; ++i) {
        //    newSessionList[i].ai = newSessionAI[i].checked;
        //}

        //var newSessionStructures = document.querySelectorAll('.new-session-structure');
        //for (i = 0; i < newSessionStructures.length; ++i) {
        //    newSessionList[i].structure = newSessionStructures[i].value;
        //}

        //var newSessionMarkets = document.querySelectorAll('.new-session-market');
        //for (i = 0; i < newSessionMarkets.length; ++i) {
        //    newSessionList[i].market = newSessionMarkets[i].value;
        //}

    });
});
