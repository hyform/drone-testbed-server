document.addEventListener("DOMContentLoaded", function (event) {
    var ajaxUrlProcess = getAjaxUrl("process");
    var activeChannel = null;
    var connection = null;
    var sessionChannelId = null;
    var space = "&nbsp;";
    var nothing = "";
    var check = "&check;";
    var responseChannel = null;
    var elapsedTime = 0;
    
    //Get a teamId for the Experimenter chat views
    var urlParams = new URLSearchParams(window.location.search);
    var teamId = null
    if (urlParams.has('teamId')) {
        teamId = urlParams.get('teamId');
    }

    // Set countdown to the number of seconds left
    function seconds_left() {
        selectAjaxUrl = ajaxUrlProcess + "elapsed_time/"
        aData = {};
        if(teamId) {
            aData = {
                csrfmiddlewaretoken: csrftoken,
                team: teamId
            }
        } else {
            aData = {
                csrfmiddlewaretoken: csrftoken
            }
        }
        //TODO: Do we want to take time here and adjust he answer below if the
        //call takes some time?
        $.ajax({
            url: selectAjaxUrl,
            method: "POST",
            data: aData,
            success: function (result) {
                var resultJson = JSON.parse(result);     
                elapsedTime = resultJson.elapsed_seconds;
                if(elapsedTime >= 0) {
                    if(teamId) {
                        var runningTimerHeader = document.getElementById('timer-header'); 
                        runningTimerHeader.removeAttribute('hidden');                        
                    }
                    var runningTimer = document.getElementById('running-timer');
                    runningTimer.removeAttribute('hidden'); 
                }
            }
        });
    }
    seconds_left();
    setInterval(function(){
        if(elapsedTime >= 0) {
            mins = Math.floor(elapsedTime / 60);
            secs = elapsedTime % 60;
            zero = "";
            if(secs < 10) {
                zero = "0";
            }
            var runningTimer = document.getElementById('running-timer');
            runningTimer.innerText = mins + ":" + zero + secs;
            elapsedTime = elapsedTime + 1;
        }
    }, 1000);

    var sendButton = $("#send");
    var messageText = $("#message");
    var designBotButton = $("#design-bot-options");
    var opsBotButton = $("#ops-bot-options");

    sendButton.prop("disabled", true);

    if ("WebSocket" in window) {
        console.log("WebSocket is supported by your Browser!");
    } else {
        console.log("WebSocket NOT supported by your Browser!");
        return;
    }

    var ajaxUrl = location.protocol + "//" + location.hostname + "/chat/channels/";
    var hPort = location.port;
    if (hPort && (hPort !== "80" || hPort !== "443")) {
        ajaxUrl = location.protocol + "//" + location.hostname + ":" + hPort + "/chat/channels/";
    }
    if (teamId) {
        ajaxUrl = ajaxUrl.concat(teamId + "/");
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

    var getChannelOnlineStatus = function (channel) {
        return (channel.childNodes[0].childNodes[0]);
    }

    var getChannelLabel = function (channel) {
        return (channel.childNodes[0].childNodes[1]);
    }

    var getPrecheckStatus = function (channel) {
        return (channel.childNodes[0].childNodes[2]);
    }

    var getPostcheckStatus = function (channel) {
        return (channel.childNodes[0].childNodes[3]);
    }

    var getChannelMessages = function (channel) {
        return (channel.childNodes[1]);
    }

    var getChannelId = function (channel) {
        return getChannelLabel(channel).id.slice("channel-".length);
    }

    var setChannelConnected = function (channel) {
        var status = getChannelOnlineStatus(channel);
        status.classList.add("is-online-yes");
        status.innerHTML = check;
    }

    var setChannelDisconnected = function (channel) {
        var status = getChannelOnlineStatus(channel);
        status.classList.remove("is-online-yes");
        status.innerHTML = nothing;
    }

    var setPrecheck = function (channel, checked) {
        var status = getPrecheckStatus(channel);
        if (checked) {
            status.classList.add("is-complete-yes");
            status.innerHTML = check;
        } else {
            status.classList.remove("is-complete-yes");
            status.innerHTML = "X";
        }
    }

    var setPostcheck = function (channel, checked) {
        var status = getPostcheckStatus(channel);
        if (checked) {
            status.classList.add("is-complete-yes");
            status.innerHTML = check;
        } else {
            status.classList.remove("is-complete-yes");
            status.innerHTML = "X";
        }
    }

    var activateChannel = function (channel) {
        var channelLabel = getChannelLabel(channel);
        var channelMessages = getChannelMessages(channel);

        if (activeChannel) {
            getChannelLabel(activeChannel).classList.remove("channel-label-active");
            getChannelLabel(activeChannel).classList.add("channel-label-default");
            getChannelMessages(activeChannel).style.display = "none";
            activeChannel.classList.remove("channel-100");
        }

        channelLabel.classList.remove("channel-label-default");
        channelLabel.classList.remove("channel-label-new-messages");
        channelLabel.classList.remove("channel-label-new-priority-messages");        
        channelLabel.classList.add("channel-label-active");
        channelMessages.style.display = "flex";
        channel.classList.add("channel-100");
        if (channelMessages.childNodes[0].hasChildNodes()) {
            channelMessages.childNodes[0].lastChild.scrollIntoView(false);
        }

        activeChannel = channel;

        //TODO: only have this for the bot structure
        if(channelLabel.innerHTML === "Design") {
            enableDesignBot();
        } else if(channelLabel.innerHTML === "Operations") {
            enableOpsBot();
        } else {
            disableBot();
        }
    };

    var send = function () {
        if (connection) {
            channelName = getChannelLabel(activeChannel).innerHTML;
            channelId = getChannelId(activeChannel);
            var messageBundle = {
                type: "message",
                channel: channelId,
                message: messageText.val(),
                channel_position: channelName,
                channel_team_id: teamId
            };
            messageText.val("");
            messageText.scrollTop(0);
            connection.send(JSON.stringify(messageBundle));
        }
    };

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

    // ---------- Bot Chat Functions ------------------    
    var clearAndAdd = function (chosenText, isDesign, temp) {
        var botChatOptions = null;
        if(isDesign) {
            botChatOptions = document.getElementById("design-bot-chat-options");
        } else {
            botChatOptions = document.getElementById("ops-bot-chat-options");
        }
        botChatOptions.innerHTML = "";
        if(chosenText) {
            currentMessage = messageText.val();
            if(currentMessage === "") {
                messageText.val(chosenText);
            } else {
                messageText.val(currentMessage + " " + chosenText);
            }
        }       
    };

    var addLabelBotChoice = function(text, isDesign, temp) {
        var botChatOptions = null;
        if(isDesign) {
            botChatOptions = document.getElementById("design-bot-chat-options");
        } else {
            botChatOptions = document.getElementById("ops-bot-chat-options");
        }
        var newBotChatOption = newBotChatOption = document.createElement("li");
        var newBotChatOptionItem = newBotChatOptionItem = document.createElement("label");        
        newBotChatOptionItem.innerHTML = text;
        newBotChatOption.appendChild(newBotChatOptionItem);
        botChatOptions.appendChild(newBotChatOption);
    };

    var addButtonBotChoice = function(text, action, isDesign, temp) {
        if(text === "range") {
            temp = temp + "range";
        } else if(text === "capacity") {
            temp = temp + "capacity";
        } else if(text === "cost") {
            temp = temp + "cost";
        }else if(text === "profit") {
            temp = temp + "profit";
        }else if(text === "customers") {
            temp = temp + "customers";
        }else if(text === "north") {
            temp = temp + "north";
        }else if(text === "south") {
            temp = temp + "south";
        }else if(text === "east") {
            temp = temp + "east";
        }else if(text === "west") {
            temp = temp + "west";
        }
        var botChatOptions = null;
        if(isDesign) {
            botChatOptions = document.getElementById("design-bot-chat-options");
        } else {
            botChatOptions = document.getElementById("ops-bot-chat-options");
        }
        var newBotChatOption = newBotChatOption = document.createElement("li");
        var newBotChatOptionItem = newBotChatOptionItem = document.createElement("button");   
        newBotChatOptionItem.classList.add("bot-choice-btn");        
        newBotChatOptionItem.innerHTML = text + " -->";
        newBotChatOptionItem.onclick = function() {
            if(text && text === "[DESIGN]") {
                addDesignSelection(action, isDesign, temp);
            } else if(text && text === "[PLAN]") {
                addPlanSelection(action, isDesign, temp);
            } else {
                action(text, isDesign, temp);
            }
        };
        newBotChatOption.appendChild(newBotChatOptionItem);
        botChatOptions.appendChild(newBotChatOption);
    };
    
    var addButtonNumber = function(action, isDesign, temp) {
        var botChatOptions = null;
        if(isDesign) {
            botChatOptions = document.getElementById("design-bot-chat-options");
        } else {
            botChatOptions = document.getElementById("ops-bot-chat-options");
        }
        var newBotChatOption = newBotChatOption = document.createElement("li");
        var newNumberLabel = newBotChatOptionItem = document.createElement("label");        
        newNumberLabel.innerHTML = "[NUMBER]";
        newBotChatOption.appendChild(newNumberLabel);
        var newNumberText = document.createElement("input");
        newNumberText.setAttribute("type", "text");
        newBotChatOption.appendChild(newNumberText);
        var newBotChatOptionItem = newBotChatOptionItem = document.createElement("button");
        newBotChatOptionItem.classList.add("bot-choice-btn");
        newBotChatOptionItem.innerHTML = " -->";
        newBotChatOptionItem.onclick = function() {
            var textValue = newNumberText.value;
            if(textValue && !isNaN(textValue)) {
                action(textValue, isDesign, temp);
            } else {
                newNumberLabel.classList.add("red-text");
            }
        };
        newBotChatOption.appendChild(newBotChatOptionItem);
        botChatOptions.appendChild(newBotChatOption);
    };    

    var addDesignSelection = function(action, isDesign, temp) {
        clearAndAdd("", isDesign, temp);

        designUrl = "/repo/vehicle/"
        designData = {
            csrfmiddlewaretoken: csrftoken
        }

        $.ajax({
            url: designUrl,
            method: "GET",
            data: designData,
            success: function (result) {
                if(result.results.length > 0) {
                    result.results.forEach(design =>
                        addButtonBotChoice("@" + design.tag, action, isDesign, temp))
                } else {
                    addLabelBotChoice("No Designs", isDesign, temp);
                    addButtonBotChoice("", action, isDesign, temp);
                }
            }
        });
    };

    var addPlanSelection = function(action, isDesign, temp) {
        clearAndAdd("", isDesign, temp);

        planUrl = "/repo/planshort/"
        planData = {
            csrfmiddlewaretoken: csrftoken
        }

        $.ajax({
            url: planUrl,
            method: "GET",
            data: planData,
            success: function (result) {
                if(result.results.length > 0) {
                    result.results.forEach(plan =>
                        addButtonBotChoice("@" + plan.tag, action, isDesign, temp))
                } else {
                    addLabelBotChoice("No Plans", isDesign, temp);
                    addButtonBotChoice("", action, isDesign, temp);
                }
            }
        });
    };
    
    var addTerminalButtonBotChoice = function(text, isDesign, temp) {        
        var botChatOptions = null;
        if(isDesign) {
            botChatOptions = document.getElementById("design-bot-chat-options");
        } else {
            botChatOptions = document.getElementById("ops-bot-chat-options");
        }
        var newBotChatOption = newBotChatOption = document.createElement("li");
        var newBotChatOptionItem = newBotChatOptionItem = document.createElement("button");
        newBotChatOptionItem.classList.add("bot-choice-btn");
        newBotChatOptionItem.innerHTML = text;
        newBotChatOptionItem.onclick = function() {
            clearAndAdd(text, isDesign, temp);
            if(isDesign) {
                $("#design-bot-chat-modal").modal("hide");
            } else {
                $("#ops-bot-chat-modal").modal("hide");
            }
        };
        newBotChatOption.appendChild(newBotChatOptionItem);
        botChatOptions.appendChild(newBotChatOption);
    };

    var addTerminalDone = function(isDesign) {
        var text = "[Done]"
        var botChatOptions = null;
        if(isDesign) {
            botChatOptions = document.getElementById("design-bot-chat-options");
        } else {
            botChatOptions = document.getElementById("ops-bot-chat-options");
        }
        var newBotChatOption = newBotChatOption = document.createElement("li");
        var newBotChatOptionItem = newBotChatOptionItem = document.createElement("button");  
        newBotChatOptionItem.classList.add("bot-choice-btn");
        newBotChatOptionItem.innerHTML = text;
        newBotChatOptionItem.onclick = function() {
            clearAndAdd("", isDesign, "");
            if(isDesign) {
                $("#design-bot-chat-modal").modal("hide");
            } else {
                $("#ops-bot-chat-modal").modal("hide");
            }
        };
        newBotChatOption.appendChild(newBotChatOptionItem);
        botChatOptions.appendChild(newBotChatOption);
    };

    // Design Bot --------------------
    var botChatWant5 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        if(!(temp.includes("range") && temp.includes("capacity") && temp.includes("cost"))) {
            addButtonBotChoice("and", botChatWant1, bot, temp);
        }
    }

    var botChatWant4 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addButtonNumber(botChatWant5, bot, temp);
    }

    var botChatWant3 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        addButtonBotChoice("than", botChatWant4, bot, temp);
        if(!(temp.includes("range") && temp.includes("capacity") && temp.includes("cost"))) {
            addButtonBotChoice("and", botChatWant1, bot, temp);
        }
    }

    var botChatWant2_2 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        addButtonBotChoice("as", botChatWant4, bot, temp);
        if(!(temp.includes("range") && temp.includes("capacity") && temp.includes("cost"))) {
            addButtonBotChoice("and", botChatWant1, bot, temp);
        }
    }

    var botChatWant2_1 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        if(!temp.includes("range")) {
            addButtonBotChoice("range", botChatWant2_2, bot, temp);
        }
        if(!temp.includes("capacity")) {
            addButtonBotChoice("capacity", botChatWant2_2, bot, temp);
        }
        if(!temp.includes("cost")) {
            addButtonBotChoice("cost", botChatWant2_2, bot, temp);
        }
    };

    var botChatWant2 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        if(!temp.includes("range")) {
            addButtonBotChoice("range", botChatWant3, bot, temp);
        }
        if(!temp.includes("capacity")) {
            addButtonBotChoice("capacity", botChatWant3, bot, temp);
        }
        if(!temp.includes("cost")) {
            addButtonBotChoice("cost", botChatWant3, bot, temp);
        }
    };

    var botChatWant1 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addButtonBotChoice("less", botChatWant2, bot, temp);
        addButtonBotChoice("more", botChatWant2, bot, temp);
        addButtonBotChoice("same", botChatWant2_1, bot, temp);
    };

    var botChatWant0 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addButtonBotChoice("want", botChatWant1, bot, temp);
    };

    var botChatPing = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalButtonBotChoice("status", bot, temp);
    };

    var designBotChatInitial = function () {
        var bot = true;
        var temp = "";
        clearAndAdd(null, bot, temp);

        addLabelBotChoice("Questions", bot, temp);
        addButtonBotChoice("[DESIGN]", botChatWant0, bot, temp);
        addButtonBotChoice("want", botChatWant1, bot, temp);
        addButtonBotChoice("ping", botChatPing, bot, temp);
        addTerminalButtonBotChoice("suggestion", bot, temp);
        addTerminalButtonBotChoice("help", bot, temp);
        addLabelBotChoice("Responses", bot, temp);
        addTerminalButtonBotChoice("no", bot, temp);
        addTerminalButtonBotChoice("unsatisfied", bot, temp);
    }

    var designBot = function () {
        $("#design-bot-chat-modal").modal();        
        designBotChatInitial();
    }

    // Ops Bot --------------------
    var opsBotChatInitial = function () {
        var bot = false;
        var temp = "";
        clearAndAdd(null, bot, temp);        

        addLabelBotChoice("Questions", bot, temp);
        addButtonBotChoice("[PLAN]", opsBotChatWant0, bot, temp);
        addButtonBotChoice("want", opsBotChatWant1, bot, temp);
        addButtonBotChoice("ping", opsBotChatPing, bot, temp);
        addTerminalButtonBotChoice("suggestion", bot, temp);
        addTerminalButtonBotChoice("help", bot, temp);
        addLabelBotChoice("Responses", bot, temp);
        addTerminalButtonBotChoice("no", bot, temp);
        addTerminalButtonBotChoice("unsatisfied", bot, temp);
    }

    var opsBotChatWant0 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addButtonBotChoice("want", opsBotChatWant1, bot, temp);
    };

    var opsBotChatWant1 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addButtonBotChoice("less", opsBotChatWant2, bot, temp);
        addButtonBotChoice("more", opsBotChatWant2, bot, temp);
        addButtonBotChoice("same", opsBotChatWant2_1, bot, temp);
    };

    var opsBotChatWant2 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        if(!temp.includes("cost")) {
            addButtonBotChoice("cost", opsBotChatWant3, bot, temp);
        }
        if(!temp.includes("profit")) {
            addButtonBotChoice("profit", opsBotChatWant3, bot, temp);
        }
        if(!temp.includes("customers")) {
            addButtonBotChoice("customers", opsBotChatWant3, bot, temp);
        }
    };

    var opsBotChatWant2_1 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        if(!temp.includes("cost")) {
            addButtonBotChoice("cost", opsBotChatWant2_2, bot, temp);
        }
        if(!temp.includes("profit")) {
            addButtonBotChoice("profit", opsBotChatWant2_2, bot, temp);
        }
        if(!temp.includes("customers")) {
            addButtonBotChoice("customers", opsBotChatWant2_2, bot, temp);
        }
    };

    var opsBotChatWant2_2 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        addButtonBotChoice("as", opsBotChatWant4, bot, temp);
        if(!(temp.includes("cost") && temp.includes("profit") && temp.includes("customers"))) {
            addButtonBotChoice("and", opsBotChatWant1, bot, temp);
        }
        addButtonBotChoice("north", opsBotChatWant6, bot, temp);
        addButtonBotChoice("south", opsBotChatWant6, bot, temp);
        addButtonBotChoice("east", opsBotChatWant6, bot, temp);
        addButtonBotChoice("west", opsBotChatWant6, bot, temp);
    };

    var opsBotChatWant3 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        addButtonBotChoice("than", opsBotChatWant4, bot, temp);
        if(!(temp.includes("cost") && temp.includes("profit") && temp.includes("customers"))) {
            addButtonBotChoice("and", opsBotChatWant1, bot, temp);
        }
        addButtonBotChoice("north", opsBotChatWant6, bot, temp);
        addButtonBotChoice("south", opsBotChatWant6, bot, temp);
        addButtonBotChoice("east", opsBotChatWant6, bot, temp);
        addButtonBotChoice("west", opsBotChatWant6, bot, temp);
    }    

    var opsBotChatWant4 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addButtonNumber(opsBotChatWant4_5, bot, temp);
    }

    var opsBotChatWant4_5 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        if(!(temp.includes("cost") && temp.includes("profit") && temp.includes("customers"))) {
            addButtonBotChoice("and", opsBotChatWant1, bot, temp);
        }
        addButtonBotChoice("north", opsBotChatWant6, bot, temp);
        addButtonBotChoice("south", opsBotChatWant6, bot, temp);
        addButtonBotChoice("east", opsBotChatWant6, bot, temp);
        addButtonBotChoice("west", opsBotChatWant6, bot, temp);
    }

    /* and not in direction choices, so remove
    var opsBotChatWant5 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        addButtonBotChoice("and", opsBotChatWant6, bot, temp);
    }
    */

    var opsBotChatWant6 = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalDone(bot);
        if(!temp.includes("north")) {
            addButtonBotChoice("north", opsBotChatWant6, bot, temp);
        }
        if(!temp.includes("south")) {
            addButtonBotChoice("south", opsBotChatWant6, bot, temp);
        }
        if(!temp.includes("east")) {
            addButtonBotChoice("east", opsBotChatWant6, bot, temp);
        }
        if(!temp.includes("west")) {
            addButtonBotChoice("west", opsBotChatWant6, bot, temp);
        }
    }

    var opsBotChatPing = function (text, bot, temp) {
        clearAndAdd(text, bot, temp);

        addTerminalButtonBotChoice("status", bot, temp);
    };

    var opsBot = function () {
        $("#ops-bot-chat-modal").modal();        
        opsBotChatInitial();
    }

    // --------

    var enableDesignBot = function () {
        document.getElementById("design-bot-div").hidden = false;
        document.getElementById("ops-bot-div").hidden = true;
    }

    var enableOpsBot = function () {
        document.getElementById("design-bot-div").hidden = true;
        document.getElementById("ops-bot-div").hidden = false;
    }

    var disableBot = function () {
        document.getElementById("design-bot-div").hidden = true;
        document.getElementById("ops-bot-div").hidden = true;
    }
    // ------------------------------------------------

    var websocketConnect = function (url) {

        connection = new WebSocket(url);

        connection.onopen = function () {
            sendButton.prop("disabled", false);
            //Remove all previous handlers. If a connection closes, multiple click handlers can be
            //handled otherwise and messages will send out multiple times
            sendButton.off();
            sendButton.on('click', send);

            messageText.off();
            messageText.keypress(function (event) {
                var keycode = (event.keyCode ? event.keyCode : event.which);
                if (keycode == '13') {
                    event.preventDefault();
                    send();
                }
            });

            designBotButton.off();
            designBotButton.on('click', designBot);
            opsBotButton.off();
            opsBotButton.on('click', opsBot);
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
            var channelId = jsonMessage.channel;
            var message = jsonMessage.message;
            var messageType = jsonMessage.type;
            var sender = jsonMessage.sender;

            // red and blue are already used
            var color_options = ['black', 'green', 'brown', 'orange', 'magenta', 'olive', 'navy', 'purple', 'teal', 'gray', 'maroon', 'aqua'];
            if(sender_color[sender] == undefined){
                var color_index = sender_index % color_options.length
                sender_color[sender] = color_options[color_index];
                sender_index += 1;
            }

            if (messageType === "chat.info") {
                // If the Session channel and no teamId, this is a regular
                // user who shouldn't get the Session message channel
                if (!teamId && message === "Session") {
                    sessionChannelId = channelId;
                    return;
                }

                var newId = "channel-" + channelId;
                var channelCheck = document.getElementById(newId);
                if (channelCheck) {
                    //New channel already exists, so don't create it again

                    //Need to clear messages though since we're connecting again and they'll be re-sent
                    channelCheck.parentNode.parentNode.childNodes[1].childNodes[0].innerHTML = '';

                    return;
                }

                var precheck = "False";
                var postcheck = "False";
                if (teamId) {
                    splitMessage = message.split("@#@");
                    if (splitMessage.length > 2) {
                        message = splitMessage[0];
                        precheck = splitMessage[1];
                        postcheck = splitMessage[2];
                    }
                }

                // Add new channel
                var channelList = document.getElementById("channel-list");

                var newChannel = document.createElement("li");
                newChannel.classList.add("channel");

                // Chat Channel Label ------------------------------
                var labelContainer = document.createElement("div");
                labelContainer.classList.add("label-container");
                newChannel.appendChild(labelContainer);

                var newChannelOnline = document.createElement("label");
                newChannelOnline.classList.add("is-online");
                newChannelOnline.innerHTML = nothing;
                labelContainer.appendChild(newChannelOnline);

                var newChannelLabel = document.createElement("label");
                newChannelLabel.id = newId;
                newChannelLabel.classList.add("channel-label");
                newChannelLabel.classList.add("channel-label-default");
                newChannelLabel.innerHTML = message;
                labelContainer.appendChild(newChannelLabel);

                newChannelLabel.onclick = function () {
                    activateChannel(this.parentNode.parentNode);
                };

                if (teamId) {
                    var newChannelPrecheck = document.createElement("label");
                    newChannelPrecheck.classList.add("is-complete");
                    if (precheck === "True") {
                        newChannelPrecheck.classList.add("is-complete-yes");
                        newChannelPrecheck.innerHTML = check;
                    } else {
                        newChannelPrecheck.innerHTML = "X";
                    }
                    labelContainer.appendChild(newChannelPrecheck);

                    var newChannelPostcheck = document.createElement("label");
                    newChannelPostcheck.classList.add("is-complete");
                    if (postcheck === "True") {
                        newChannelPostcheck.classList.add("is-complete-yes");
                        newChannelPostcheck.innerHTML = check;
                    } else {
                        newChannelPostcheck.innerHTML = "X";
                    }
                    labelContainer.appendChild(newChannelPostcheck);
                }

                // Chat Channel messages ----------------------------------
                var newChannelMessages = document.createElement("div");
                newChannelMessages.classList.add("message-list-container");
                newChannelMessages.style.display = "none";
                newChannel.appendChild(newChannelMessages);

                var newChannelMessageList = document.createElement("ul");
                newChannelMessageList.id = "messages-" + channelId;
                newChannelMessageList.classList.add("list-unstyled");
                newChannelMessageList.classList.add("message-list");
                newChannelMessages.append(newChannelMessageList);

                if (message === "Help" || message === "Session") {
                    //If the Setup channel is added back in, place it before these two
                    channelList.appendChild(newChannel);
                    activateChannel(channelList.children[0]);
                    if(message === "Help") {
                        responseChannel = channelId;
                    }
                } else {
                    if (channelList.hasChildNodes) {
                        var channels = channelList.children;
                        var found = false;
                        for (var i = 0; i < channels.length; i++) {
                            var channel = channels[i];
                            if (channel.hasChildNodes) {
                                var label = channel.firstChild;
                                if (message <= label.innerText) {
                                    channelList.insertBefore(newChannel, channel);
                                    found = true;
                                    break;
                                }
                            }
                        }
                        if (!found) {
                            channelList.appendChild(newChannel);
                        }
                    } else {
                        channelList.appendChild(newChannel);
                        activateChannel(newChannel);
                    }
                }
            } else if (messageType === "system.command") {
                if (message.startsWith("refresh")) {
                    //if (teamId && message.endsWith("exper")) {
                    if (teamId) {
                        // Experimemter chat should only reload itself, not the whole page
                        location.reload();
                    //} else if (teamId) {
                        // do nothing in this case
                    } else {
                        parent.location.reload();
                    }
                }
            } else if (messageType === "session.request" && teamId) {
                // Do nothin in this case
            } else if (messageType === "session.request" && !teamId) {
                var message = jsonMessage.message;
                if (message === "respond") {
                    sendResponse(channelId);
                }
            } else if (messageType === "session.response" && teamId) {
                var channelList = document.getElementById("channel-list");
                if (channelList.hasChildNodes) {
                    var channels = channelList.children;
                    for (var i = 0; i < channels.length; i++) {
                        var channel = channels[i];
                        if (channelId === getChannelId(channel)) {
                            var label = getChannelLabel(channel);
                            if (message === "connected") {
                                setChannelConnected(channel);
                            } else if (message === "disconnected") {
                                setChannelDisconnected(channel);
                            }
                        }
                    }
                }
            } else if (messageType === "session.response" && !teamId) {
                // Do nothin in this case
            } else if (messageType === "system.usermessage" && !teamId) {
                // System message for a non-exper user, so stick in all channels
                var channelList = document.getElementById("channel-list");
                if (channelList.hasChildNodes) {
                    var channels = channelList.children;
                    for (var i = 0; i < channels.length; i++) {
                        var newMessage = document.createElement("li");
                        var timerText = "";
                        var runningTimer = document.getElementById('running-timer');
                        if(!runningTimer) {
                            runningTimer = document.getElementById('running-timer-exper');
                            timerText = runningTimer.innerText;
                        } else {
                            timerText = runningTimer.innerText;
                        }
                        var newMessageText = timerText + " " + '<b style="color:blue">' + sender + ' : </b>' + message;
                        newMessage.innerHTML = newMessageText;
                        var channel = channels[i];
                        var channelMessages = getChannelMessages(channel);
                        channelMessages.childNodes[0].appendChild(newMessage);
                        newMessage.scrollIntoView(false);
                    }
                }
                //This is a scenario/plan/design update, so tell the unity component to refresh its views
                if(window.parent.gameInstance) {
                    //Just try update for both ops/business and designer
                    //TODO: only call the correct one here to prevent unintentional side effects down the road
                    try {
                        window.parent.gameInstance.SendMessage('groundcube', 'updatePlansAndDesigns');
                    } catch(err) {
                        //Expecting an error on one of these, so don't log unless debugging
                        //console.log(err);
                    }
                    try {
                        window.parent.gameInstance.SendMessage('GUI', 'updateDesigns');
                    } catch(err) {
                        //Expecting an error on one of these, so don't log unless debugging
                        //console.log(err);
                    }
                }
            } else if (messageType === "system.usermessage" && teamId) {
                // System message for a exper
                var channelList = document.getElementById("channel-list");
                if (channelList.hasChildNodes) {
                    var channels = channelList.children;
                    for (var i = 0; i < channels.length; i++) {
                        var channel = channels[i];
                        if (channelId === getChannelId(channel)) {
                            var newMessage = document.createElement("li");
                            var timerText = "";
                            var runningTimer = document.getElementById('running-timer');
                            if(!runningTimer) {
                                runningTimer = document.getElementById('running-timer-exper');
                                timerText = runningTimer.innerText;
                            } else {
                                timerText = runningTimer.innerText;
                            }
                            var newMessageText = timerText + " " + '<b style="color:blue">' + sender + ' : </b>' + message;
                            newMessage.innerHTML = newMessageText;
                            var channelMessages = getChannelMessages(channel);
                            channelMessages.childNodes[0].appendChild(newMessage);
                            newMessage.scrollIntoView(false);
                        }
                    }
                }
            } else if (messageType === "user.precheck") {
                if (teamId) { //for experimenters only
                    var channelList = document.getElementById("channel-list");
                    if (channelList.hasChildNodes) {
                        var channels = channelList.children;
                        for (var i = 0; i < channels.length; i++) {
                            var channel = channels[i];
                            if (channelId === getChannelId(channel)) {
                                var label = getChannelLabel(channel);
                                if (message) {
                                    setPrecheck(channel, true);
                                } else {
                                    setPrecheck(channel, false);
                                }
                            }
                        }
                    }
                }
            } else if (messageType == "user.postcheck") {
                if (teamId) { //for experimenters only
                    var channelList = document.getElementById("channel-list");
                    if (channelList.hasChildNodes) {
                        var channels = channelList.children;
                        for (var i = 0; i < channels.length; i++) {
                            var channel = channels[i];
                            if (channelId === getChannelId(channel)) {
                                var label = getChannelLabel(channel);
                                if (message) {
                                    setPostcheck(channel, true);
                                } else {
                                    setPostcheck(channel, false);
                                }
                            }
                        }
                    }
                }
            } else if (channelId === sessionChannelId) {
                var channelList = document.getElementById("channel-list");
                if (channelList.hasChildNodes) {
                    var channels = channelList.children;
                    for (var i = 0; i < channels.length; i++) {
                        var newMessage = document.createElement("li");
                        var timerText = "";
                        var runningTimer = document.getElementById('running-timer');
                        if(!runningTimer) {
                            runningTimer = document.getElementById('running-timer-exper');
                            timerText = runningTimer.innerText;
                        } else {
                            timerText = runningTimer.innerText;
                        }
                        var newMessageText = timerText + " " + '<b style="color:red">' + sender + ' : </b>' + message;
                        newMessage.innerHTML = newMessageText;
                        var channel = channels[i];
                        var channelMessages = getChannelMessages(channel);
                        channelMessages.childNodes[0].appendChild(newMessage);
                        newMessage.scrollIntoView(false);
                    }
                }
            } else {
                var channelList = document.getElementById("channel-list");
                if (channelList.hasChildNodes) {
                    var channels = channelList.children;
                    for (var i = 0; i < channels.length; i++) {
                        var channel = channels[i];
                        var thisChannelId = getChannelId(channel);
                        if (channelId === thisChannelId) {
                            if (channel === activeChannel) {
                                var newMessage = document.createElement("li");
                                var timerText = "";
                                var runningTimer = document.getElementById('running-timer');
                                if(!runningTimer) {
                                    runningTimer = document.getElementById('running-timer-exper');
                                    timerText = runningTimer.innerText;
                                } else {
                                    timerText = runningTimer.innerText;
                                }
                                var newMessageText = timerText + " " + '<b style="color:' + sender_color[sender] + '">' + sender + ' : </b>' + message;
                                newMessage.innerHTML = newMessageText;
                                if((sender === "Process Manager") && !teamId) {
                                    var audio = new Audio('/static/audio/priority_message_notification.mp3');
                                    audio.play();
                                }
                                var channelMessages = getChannelMessages(channel);
                                channelMessages.childNodes[0].appendChild(newMessage);
                                newMessage.scrollIntoView(false);
                            } else {
                                var newMessage = document.createElement("li");
                                var timerText = "";
                                var runningTimer = document.getElementById('running-timer');
                                if(!runningTimer) {
                                    runningTimer = document.getElementById('running-timer-exper');
                                    timerText = runningTimer.innerText;
                                } else {
                                    timerText = runningTimer.innerText;
                                }
                                var newMessageText = timerText + " " + '<b style="color:' + sender_color[sender] + '">' + sender + ' : </b>' + message;
                                newMessage.innerHTML = newMessageText;
                                if((sender === "Process Manager") && !teamId) {
                                    console.log("priority message");
                                    getChannelLabel(channel).classList.add("channel-label-new-priority-messages");
                                    var audio = new Audio('/static/audio/priority_message_notification.mp3');
                                    audio.play();
                                } else {
                                    console.log("regular message");
                                    getChannelLabel(channel).classList.add("channel-label-new-messages");
                                }
                                var channelMessages = getChannelMessages(channel);
                                channelMessages.childNodes[0].appendChild(newMessage);
                                newMessage.scrollIntoView(false);
                            }
                        }
                    }
                }
            }
        };
    };

    //start things rolling
    $.ajax({
        url: ajaxUrl, success: function (result) {
            var url = getWsURL();
            if (teamId) {
                url = url.concat("?teamId=" + teamId);
            }
            websocketConnect(url);
        }
    });

    //start periodic response
    setInterval(function() {
        if(responseChannel && !teamId) {
            sendResponse(responseChannel);
        }
    }, 15 * 1000);


});
