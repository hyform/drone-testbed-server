document.addEventListener("DOMContentLoaded", function (event) {
    var ajaxUrl = getAjaxUrl("process");

    function intervention_handler(event) {
        selectAjaxUrl = ajaxUrl + "intervention/"
        $.ajax({
            url: selectAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
                intervention: event.data.intervention
            },
            success: function (result) {
                //call function to disable buttons
            }
        });
    }

    $("#inter-1").click({intervention: 1}, intervention_handler);
    $("#inter-2").click({intervention: 2}, intervention_handler);
    $("#inter-3").click({intervention: 3}, intervention_handler);
    $("#inter-4").click({intervention: 4}, intervention_handler);
    $("#inter-5").click({intervention: 5}, intervention_handler);
    $("#inter-6").click({intervention: 6}, intervention_handler);
    $("#inter-7").click({intervention: 7}, intervention_handler);
    $("#inter-8").click({intervention: 8}, intervention_handler);
    $("#inter-9").click({intervention: 9}, intervention_handler);
    $("#inter-10").click({intervention: 10}, intervention_handler);
    $("#inter-11").click({intervention: 11}, intervention_handler);
    $("#inter-12").click({intervention: 12}, intervention_handler);
    $("#inter-13").click({intervention: 13}, intervention_handler);
    
    var elapsedTime = null;
    var timeLeft = null;
    var countdown = null;
    function elapsed_time() {
        selectAjaxUrl = ajaxUrl + "elapsed_time/"
        $.ajax({
            url: selectAjaxUrl,
            method: "POST",
            data: {
                csrfmiddlewaretoken: csrftoken,
            },
            success: function (result) {
                var resultJson = JSON.parse(result);
                elapsedTime = resultJson.elapsed_time;
                timeLeft = 900 - parseInt(elapsedTime);
                countdown = timeLeft;
            }
        });
    }

    //elapsed_time();
    /*
    countdown = 900;

    var timer = document.getElementById("timer");
    setInterval(function(){ 
        timer.innerText = countdown;
        countdown = countdown - 1;
    }, 1000);
    */

    var connection = null;
    var sessionChannelId = null;
    var responseChannel = null;
    var designerChannelId = "";
    var operationsChannelId = "";
    var designerManagementChannelId = "";
    var operationsManagementChannelId = "";
    var helpChannelId = "";    

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
        var wsurl = protocol + "//" + location.hostname + "/ws/chat/";
        var wPort = location.port;
        if (wPort && (wPort !== "80" || wPort !== "443")) {
            wsurl = protocol + "//" + location.hostname + ":" + wPort + "/ws/chat/";
        }
        return wsurl;
    }

    var sendResponse = function (channelId) {
        if (connection) {
            var messageBundle = {
                type: "session.response",
                channel: channelId,
                message: "connected",
            };
            connection.send(JSON.stringify(messageBundle));
        }
    }

    var last1 = "";
    var c1 = 1;
    var last2 = "";
    var c2 = 1;
    var last3 = "";
    var c3 = 1;
    var last4 = "";
    var c4 = 1;

    var websocketConnect = function (url) {

        connection = new WebSocket(url);

        connection.onopen = function () {
        };

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

        var sender_color = {}
        var sender_index = 0;

        connection.onmessage = function (event) {
            var jsonMessage = JSON.parse(event.data);
            var messageType = jsonMessage.type;
            var channelId = jsonMessage.channel;
            
            //TODO: is sender always available? Check new messsage types
            var sender = jsonMessage.sender;

            // red and blue are already used
            var color_options = ['black', 'green', 'brown', 'orange', 'magenta', 'olive', 'navy', 'purple', 'teal', 'gray', 'maroon', 'aqua'];
            if(sender_color[sender] == undefined){
                var color_index = sender_index % color_options.length
                sender_color[sender] = color_options[color_index];
                sender_index += 1;
            }

            if (messageType === "event.info") {                
                var position = jsonMessage.position;
                var info = jsonMessage.info;

                //TODO: session get time from actual message
                var date = new Date();
                var hours = date.getHours();
                var minutes = date.getMinutes();

                if(position === "Designer 1")
                {
                    var newMessage = document.createElement("li");
                    var newMessageText = hours + ":" + minutes + " " + info;
                    console.log(info);

                    if(info === last1) {
                        c1 = c1+1;
                        newMessageText = newMessageText + " (" + c1 + ")";
                    } else {
                        last1 = info;
                        c1 = 1;
                    }
                    newMessage.innerHTML = newMessageText;
                    
                    var messageList = document.getElementById("message-list-1");
                    if(c1 > 1) {
                        messageList.replaceChild(newMessage, messageList.childNodes[messageList.childElementCount - 1]);
                    } else {
                        messageList.appendChild(newMessage);
                    }
                    newMessage.scrollIntoView(false);
                }

                if(position === "Designer 2")
                {
                    var newMessage = document.createElement("li");
                    var newMessageText = hours + ":" + minutes + " " + info;
                    console.log(info);

                    if(info === last2) {
                        c2 = c2+1;
                        newMessageText = newMessageText + " (" + c2 + ")";
                    } else {
                        last2 = info;
                        c2 = 1;
                    }
                    newMessage.innerHTML = newMessageText;
                    
                    var messageList = document.getElementById("message-list-2");
                    if(c2 > 1) {
                        messageList.replaceChild(newMessage, messageList.childNodes[messageList.childElementCount - 1]);
                    } else {
                        messageList.appendChild(newMessage);
                    }
                    newMessage.scrollIntoView(false);
                }

                if(position === "Ops Planner 1")
                {
                    var newMessage = document.createElement("li");
                    var newMessageText = hours + ":" + minutes + " " + info;
                    console.log(info);

                    if(info === last3) {
                        c3 = c3+1;
                        newMessageText = newMessageText + " (" + c3 + ")";
                    } else {
                        last3 = info;
                        c3 = 1;
                    }
                    newMessage.innerHTML = newMessageText;
                    
                    var messageList = document.getElementById("message-list-3");
                    if(c3 > 1) {
                        messageList.replaceChild(newMessage, messageList.childNodes[messageList.childElementCount - 1]);
                    } else {
                        messageList.appendChild(newMessage);
                    }
                    newMessage.scrollIntoView(false);
                }

                if(position === "Ops Planner 2")
                {
                    var newMessage = document.createElement("li");
                    var newMessageText = hours + ":" + minutes + " " + info;
                    console.log(info);

                    if(info === last4) {
                        c4 = c4+1;
                        newMessageText = newMessageText + " (" + c4 + ")";
                    } else {
                        last4 = info;
                        c4 = 1;
                    }
                    newMessage.innerHTML = newMessageText;
                    
                    var messageList = document.getElementById("message-list-4");
                    if(c4 > 1) {
                        messageList.replaceChild(newMessage, messageList.childNodes[messageList.childElementCount - 1]);
                    } else {
                        messageList.appendChild(newMessage);
                    }
                    newMessage.scrollIntoView(false);
                }
            } else if (messageType === "chat.info") {
                var message = jsonMessage.message;
                // If the Session channel and no teamId, this is a regular
                // user who shouldn't get the Session message channel
                if (message === "Session") {
                    sessionChannelId = channelId;
                } else if (message === "Designer") {
                    designerChannelId = channelId;
                } else if (message === "Operations") {
                    operationsChannelId = channelId;
                } else if (message === "Designer Management") {
                    designerManagementChannelId = channelId;
                } else if (message === "Operations Management") {
                    operationsManagementChannelId = channelId;
                } else if (message === "Help") {
                    helpChannelId = channelId;
                    responseChannel = channelId;
                }

                /* Do we need to do something with this?
                var newId = "channel-" + channelId;
                var channelCheck = document.getElementById(newId);
                if (channelCheck) {
                    //New channel already exists, so don't create it again

                    //Need to clear messages though since we're connecting again and they'll be re-sent
                    channelCheck.parentNode.parentNode.childNodes[1].childNodes[0].innerHTML = '';

                    return;
                }
                */                                
            } else if (messageType === "system.command") {
                var message = jsonMessage.message;
                if (message.startsWith("refresh")) {
                    parent.location.reload();
                }
            } else if (messageType === "session.request") {
                var message = jsonMessage.message;
                if (message === "respond") {
                    sendResponse(channelId);
                }
            } else if (messageType === "session.response") {
                // Do nothin in this case
            } else if (messageType === "system.usermessage") {
                var message = jsonMessage.message;
                var newMessage = document.createElement("li");
                var newMessageText = '<b style="color:blue">' + sender + ' : </b>' + message;
                newMessage.innerHTML = newMessageText;
                var channelMessages = getElementById("chat-list-5");
                channelMessages.childNodes[0].appendChild(newMessage);
                newMessage.scrollIntoView(false);
            } else if (channelId === sessionChannelId) {
                var message = jsonMessage.message;
                var newMessage = document.createElement("li");
                var newMessageText = '<b style="color:red">' + sender + ' : </b>' + message;
                newMessage.innerHTML = newMessageText;
                var channel = channels[i];
                var channelMessages = getElementById("chat-list-5");
                channelMessages.childNodes[0].appendChild(newMessage);
                    newMessage.scrollIntoView(false);
            } else if (messageType === "chat.message") {
                var message = jsonMessage.message;
                var newMessage = document.createElement("li");
                var newMessageText = '<b style="color:' + sender_color[sender] + '">' + sender + ' : </b>' + message;
                newMessage.innerHTML = newMessageText;
                chatId = "";
                if(channelId === designerChannelId) {
                    chatId = "chat-list-1";
                } else if(channelId === operationsChannelId) {
                    chatId = "chat-list-2";
                } if(channelId === designerManagementChannelId) {
                    chatId = "chat-list-3";
                } if(channelId === operationsManagementChannelId) {
                    chatId = "chat-list-4";
                } if(channelId === helpChannelId) {
                    chatId = "chat-list-5";
                }
                var channelMessages = document.getElementById(chatId);
                channelMessages.appendChild(newMessage);
                newMessage.scrollIntoView(false);
            }
        };
    };

    //start things rolling
    $.ajax({
        url: ajaxUrl, success: function (result) {
            var url = getWsURL();
            websocketConnect(url);
        }
    });

    //start periodic response
    setInterval(function() {
        if(responseChannel) {
            sendResponse(responseChannel);
        }
    }, 15 * 1000);

});