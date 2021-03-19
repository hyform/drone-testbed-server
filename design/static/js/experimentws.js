document.addEventListener("DOMContentLoaded", function (event) {
    var connection = null;  

    if ("WebSocket" in window) {
        console.log("WebSocket is supported by your Browser!");
    } else {
        console.log("WebSocket NOT supported by your Browser!");
        return;
    }

    var getWsURL = function () {
        var protocol = "";
        if (location.protocol === "http:") {
            protocol = "ws:";
        } else if (location.protocol === "https:") {
            protocol = "wss:";
        }
        var wsurl = protocol + "//" + location.hostname + "/ws/org/";
        var wPort = location.port;
        if (wPort && (wPort !== "80" || wPort !== "443")) {
            wsurl = protocol + "//" + location.hostname + ":" + wPort + "/ws/org/";
        }
        return wsurl;
    }

    var websocketConnect = function (url) {

        connection = new WebSocket(url);

        connection.onclose = function (e) {
            console.log('Websocket closed. Attempt to reconnect in 1 seconds', e.reason);
            setTimeout(function () {
                websocketConnect(url);
            }, 1000);
        };

        connection.onerror = function (error) {
            console.log('WebSocket Error ', error);
            connection.close();
        };

        connection.onmessage = function (event) {
            var jsonMessage = JSON.parse(event.data);
            var messageType = jsonMessage.type;
            var message = jsonMessage.message;

            if (messageType === "system.command") {
                if (message === "experimenter-reload") {
                    location.reload();
                }
            }
        };
    };

    websocketConnect(getWsURL());
});