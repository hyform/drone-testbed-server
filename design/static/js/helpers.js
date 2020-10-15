
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var ajaxUrl = location.protocol + "//" + location.hostname + "/repo/vehicle/";
var hPort = location.port;
if (hPort && (hPort !== "80" || hPort !== "443")) {
    ajaxUrl = location.protocol + "//" + location.hostname + ":" + hPort + "/repo/vehicle/";
}

var ajaxUrlDataLog = location.protocol + "//" + location.hostname + "/repo/datalog/";
if (hPort && (hPort !== "80" || hPort !== "443")) {
    ajaxUrlDataLog = location.protocol + "//" + location.hostname + ":" + hPort + "/repo/datalog/";
}

counter = 0;
function savevehicle(config, range, capacity, cost, velocity){
  counter += 1;
  var design_tag = prompt("Enter design tag", "dronebot" + counter);
  if(design_tag != null){
    $.ajax({
        url: ajaxUrl,
        method: "POST",
        data: {
            csrfmiddlewaretoken: csrftoken,
            tag: design_tag,
            config: config,
            result: "DroneBotDesign",
            range: range,
            velocity: velocity,
            cost: cost,
            payload: capacity
        },
        error: function(xhr, status, error) {
          var err = eval("(" + xhr.responseText + ")");
          alert(err.Message);
        },
        success: function (result) {
          $.ajax({
              url: ajaxUrlDataLog,
              method: "POST",
              data: {
                  csrfmiddlewaretoken: csrftoken,
                  action: "SelectedDroneBotDesign;tag=" + design_tag + ";range=" + range + ";capacity=" + capacity + ";cost=" + cost + ";velocity=" + velocity,
                  type: "DroneBotDesign",
              },
              error: function(xhr, status, error) {
                var err = eval("(" + xhr.responseText + ")");
                alert(err.Message);
              },
              success: function (result) {
              }

          });
        }

    });





  }

}
