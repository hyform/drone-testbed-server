$(document).ready(function () {
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

    var ajaxUrl = location.protocol + "//" + location.hostname + "/exper/";
	var hPort = location.port;
	if(hPort && (hPort !== "80" || hPort !== "443")) {
		ajaxUrl = location.protocol + "//" + location.hostname + ":" + hPort + "/exper/";
	}

    $('#pre-user-complete').on('click', function () {
        stopAjaxUrl = ajaxUrl + "pre_check/";
        isChecked = $('#pre-user-complete').prop("checked");
        $.ajax({
            url: stopAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
                is_checked: isChecked
            }
        });
    });

    $('#post-user-complete').on('click', function () {
        stopAjaxUrl = ajaxUrl + "post_check/";
        isChecked = $('#post-user-complete').prop("checked");
        $.ajax({
            url: stopAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
                is_checked: isChecked
            }
        });
    });
});