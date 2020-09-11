$(document).ready(function () {
    
    var ajaxUrl = getAjaxUrl("exper");

    var positionData = [];
    var channelData = {};

    $('#add_position_button').on('click', function () {
        var positionList = document.getElementById("position_list");
        var newPosition = document.createElement("li");
        var positionName = document.getElementById("position-name").value;
        var role = document.getElementById("select-role");
        var roleName = role.options[role.selectedIndex].text;
        var fullName = positionName + " (" + roleName + ")";
        newPosition.innerHTML = fullName;
        positionList.appendChild(newPosition);
        var pos = {};
        pos['role'] = roleName;
        pos['name'] = positionName;
        positionData.push(pos);
        
        var channelPositionList = document.getElementById("channel_position_list");
        var newChannelPosition = document.createElement("li");
        var checkBox = document.createElement("input");
        checkBox.id = "position_" + positionName;
        checkBox.setAttribute("type", "checkbox");
        checkBox.setAttribute("value", JSON.stringify(pos));
        
        var checkBoxLabel = document.createElement("label");
        checkBoxLabel.setAttribute("for", "position_" + positionName);
        checkBoxLabel.innerHTML = fullName

        newChannelPosition.appendChild(checkBox);
        newChannelPosition.appendChild(checkBoxLabel);
        channelPositionList.appendChild(newChannelPosition);
    });

    $('#add_channel_button').on('click', function () {
        var channelList = document.getElementById("channel_list");
        var newChannel = document.createElement("li");
        var channelName = document.getElementById("channel-name").value;
        newChannel.innerHTML = channelName;
        channelList.appendChild(newChannel);

        var positionsForChannel = [];
        var channelPositionList = document.getElementById("channel_position_list");
        var boxes = channelPositionList.getElementsByTagName("li");
        for(var i = 0; i < boxes.length; ++i) {
            var checkBox = boxes[i].childNodes[0];
            if(checkBox.checked == true) {
                var checkBoxValue = checkBox.value;
                var obj = JSON.parse(checkBoxValue);
                positionsForChannel.push(obj);                
            }
        }

        var newChannelData = {};
        newChannelData['name'] = channelName;
        newChannelData['data'] = positionsForChannel;
        
        channelData['positions'] = positionData;
        channelData['channels'] = newChannelData;
    });

    $('#create_structure_button').on('click', function () {
        structureAjaxUrl = ajaxUrl + "create_structure/"
        $.ajax({
            url: structureAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
                channelData: JSON.stringify(channelData)
            }
        });
    });
});