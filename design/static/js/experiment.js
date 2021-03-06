$(document).ready(function () {
    var ajaxUrl = getAjaxUrl("exper");

    function getId(thiss) {
        thisId = $(thiss).attr('id');
        idSplit = thisId.split("_");
        idSplitId = idSplit[idSplit.length - 1];
        return idSplitId;
    }

    $('#change_selection_button').on('click', function () {
        selectAjaxUrl = ajaxUrl + "change_selection/"
        $.ajax({
            url: selectAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
            },
            success: function (result) {
                window.location.href = "/experiment";
            }
        });
    });

    $('.play_button').on('click', function () {
        playAjaxUrl = ajaxUrl + "session_status_play/"
        gottenId = getId(this);
        statusId = "#status_" + gottenId;
        buttonId = "#play_button_" + gottenId;
        infoId = "#info_text_" + gottenId;

        //Check archive attempt first
        if ($(statusId).text() === "After" && $(buttonId).text() === "Archive") {
            var choice = confirm("Archive Session?\nThe Session will no longer be playable!");
            if (choice == true) {
                archiveAjaxUrl = ajaxUrl + "session_status_archive/"
                gottenId = getId(this);
                statusId = "#status_" + gottenId;
                $.ajax({
                    url: archiveAjaxUrl,
                    method: "PUT",
                    data: {
                        csrfmiddlewaretoken: csrftoken,
                        id: gottenId,
                        newstatus: 5,
                        goto_next: true
                    },
                    success: function (result) {
                        $(statusId).removeClass('running-status').removeClass('stopped-status').removeClass('setup-status').removeClass('presession-status').removeClass('postsession-status');
                        $(statusId).addClass('archived-status');
                        $(statusId).text("Archived");
                        $(buttonId).text("Archived");
                        $(buttonId).prop('disabled', true);
                        $(infoId).html("Archived Sesson");

                        stopButtonId = "#stop_button_" + gottenId;
                        archiveButtonId = "#archive_button_" + gottenId;
                        $(stopButtonId).prop('disabled', true);
                        $(archiveButtonId).prop('disabled', true);

                        if (result.hasOwnProperty("next_id")) {
                            var nextId = result.next_id;
                            nestStatusId = "#status_" + nextId;
                            nextButton_d = "#play_button_" + nextId;
                            nextInfoId = "#info_text_" + nextId;

                            $(nestStatusId).removeClass('running-status').removeClass('stopped-status').removeClass('setup-status').removeClass('presession-status').removeClass('postsession-status');
                            $(nestStatusId).addClass('presession-status');
                            $(nestStatusId).text("Before");
                            $(nextButton_d).text("Next");
                            $(nextInfoId).html("Continue to the <b>Exercise</b>");
                        }
                    }
                });
            } else {
                return;
            }
        } else {

            $.ajax({
                url: playAjaxUrl,
                method: "PUT",
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    id: gottenId
                },
                success: function (result) {
                    var newStatus = JSON.parse(result["new_status"]);
                    var hasNext = JSON.parse(result["has_next"]);
                    $(statusId).removeClass('running-status').removeClass('stopped-status').removeClass('setup-status').removeClass('presession-status').removeClass('postsession-status');
                    if (newStatus === 1) {
                        $(statusId).addClass('running-status');
                        $(statusId).text("Running");
                        $(buttonId).text("Next");
                        $(infoId).html("Continue to <b>Post-Session</b>");
                    } else if (newStatus === 4) {
                        $(statusId).addClass('stopped-status');
                        $(statusId).text("Stopped");
                        $(buttonId).text("Play");
                        $(infoId).html("Activate the Session and enter <b>Setup</b>");
                    } else if (newStatus === 5) {
                        $(statusId).addClass('archived-status');
                        $(statusId).text("Archived");
                        $(buttonId).text("Archived");
                        $(buttonId).prop('disabled', true);
                        $(infoId).html("Archived Sesson");
                    } else if (newStatus === 6) {
                        $(statusId).addClass('setup-status');
                        $(statusId).text("Setup");
                        $(buttonId).text("Next");
                        $(infoId).html("Continue to <b>Pre-Session</b>");
                    } else if (newStatus === 7) {
                        $(statusId).addClass('presession-status');
                        $(statusId).text("Before");
                        $(buttonId).text("Next");
                        $(infoId).html("Continue to the <b>Exercise</b>");
                    } else if (newStatus === 8) {
                        $(statusId).addClass('postsession-status');
                        $(statusId).text("After");
                        $(buttonId).text("Archive");
                        if (hasNext) {
                            $(infoId).html("<b>Archive</b> the Session and continue to the next Session");
                        } else {
                            $(infoId).html("<b>Archive</b> the Session and end the Exercise");
                        }
                    }
                },
                error: function (xhr, status, error) {
                    if (xhr.status === 409) {
                        alert("Cannot start.\n\nA team in this session is already in an active session")
                    } else {
                        alert(xhr.responseText);
                    }
                }
            });
        }
    });

    $('.stop_button').on('click', function () {
        stopAjaxUrl = ajaxUrl + "session_status_stop/"
        gottenId = getId(this);
        statusId = "#status_" + gottenId;
        buttonId = "#play_button_" + gottenId;
        infoId = "#info_text_" + gottenId;
        $.ajax({
            url: stopAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
                id: gottenId,
                newstatus: 4
            },
            success: function (result) {
                $(statusId).removeClass('running-status').removeClass('stopped-status').removeClass('setup-status').removeClass('presession-status').removeClass('postsession-status');
                $(statusId).addClass('stopped-status');
                $(statusId).text("Stopped");
                $(buttonId).text("Play");
                $(infoId).html("Activate the Session and enter <b>Setup</b>");
            }
        });
    });

    $('.archive_button').on('click', function () {
        var choice = confirm("Archive Session?\nThe Session will no longer be playable!");
        if (choice == true) {
            archiveAjaxUrl = ajaxUrl + "session_status_archive/"
            gottenId = getId(this);
            statusId = "#status_" + gottenId;
            $.ajax({
                url: archiveAjaxUrl,
                method: "PUT",
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    id: gottenId,
                    newstatus: 5
                },
                success: function (result) {
                    buttonId = "#play_button_" + gottenId;
                    infoId = "#info_text_" + gottenId;

                    $(statusId).removeClass('running-status').removeClass('stopped-status').removeClass('setup-status').removeClass('presession-status').removeClass('postsession-status');
                    $(statusId).addClass('archived-status');
                    $(statusId).text("Archived");
                    $(buttonId).text("Archived");
                    $(buttonId).prop('disabled', true);
                    $(infoId).html("Archived Sesson");

                    stopButtonId = "#stop_button_" + gottenId;
                    archiveButtonId = "#archive_button_" + gottenId;
                    $(stopButtonId).prop('disabled', true);
                    $(archiveButtonId).prop('disabled', true);
                }
            });
        }
    });

    //---------------------------------
    $('#change_user_password_button').on('click', function () {
        passAjaxUrl = ajaxUrl + "change_user_password/"
        var newpassword = $('#new-user-password').val();
        var newpasswordId = $("#select-password-user option:selected").val();
        if(newpassword !== "") {
            $.ajax({
                url: passAjaxUrl,
                method: "PUT",
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    newpassword: newpassword,
                    newpassword_id: newpasswordId
                },
                error: function (result) {
                    $('#user-password-change-status').replaceWith('<div id="user-password-change-status">Password change failed</div>')
                },
                success: function (result) {
                    $('#user-password-change-status').replaceWith('<div id="user-password-change-status">Password change complete</div>')
                }
            });
        }
    });

    $('#change_password_button').on('click', function () {
        passAjaxUrl = ajaxUrl + "change_org_password/"
        var newpassword = $('#new-password').val();
        if(newpassword != "") {
            $.ajax({
                url: passAjaxUrl,
                method: "PUT",
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    newpassword: newpassword
                },
                error: function (result) {
                    $('#password-change-status').replaceWith('<div id="password-change-status">Password change failed</div>')
                },
                success: function (result) {
                    $('#password-change-status').replaceWith('<div id="password-change-status">Password change complete</div>')
                }
            });
        }
    });

    //----------------------------------
    
    $('#add_session_button').on('click', function () {
        sessionNameNew = $("#session-name-new").val();
        sessionAINew = $("#session-ai-new").prop("checked");
        sessionStructureIdNew = $("#select-structure-new option:selected").val();
        sessionMarketIdNew = $("#select-market-new option:selected").val();

        if(!sessionNameNew) {
            alert("Please enter a name for the new Session");
            return;
        }

        var sessionList = document.getElementById("session-list");

        //TODO:This isn't incrementing
        var numNewSessions = document.querySelectorAll('.new-session').length;
        var newSessionIndex = numNewSessions + 1;

        var newSession = document.createElement("div");
        newSession.classList.add("new-session");
        newSession.id = "new-session-" + newSessionIndex;

        var newSessionBorder = document.createElement("div");
        newSessionBorder.classList.add("border-session");
        newSession.appendChild(newSessionBorder);

        //new name
        var nameRow = document.createElement("div");
        nameRow.classList.add("row");
        newSessionBorder.appendChild(nameRow);

        var nameRowLabelCol = document.createElement("div");
        nameRowLabelCol.classList.add("col-3");
        nameRow.appendChild(nameRowLabelCol);

        var nameRowLabel = document.createElement("label");
        nameRowLabel.htmlFor = "session-name-" + newSessionIndex;
        nameRowLabel.innerHTML = "Name"
        nameRowLabelCol.appendChild(nameRowLabel);

        var nameRowInputCol = document.createElement("div");
        nameRowInputCol.classList.add("col-9");
        nameRow.appendChild(nameRowInputCol);

        var nameRowInput = document.createElement("input");
        nameRowInput.classList.add("form-control");
        nameRowInput.classList.add("new-session-name");
        nameRowInput.id = "session-name-" + newSessionIndex;
        nameRowInput.type = "text"
        nameRowInput.value = sessionNameNew
        nameRowInputCol.appendChild(nameRowInput);

        //new AI
        var aiRow = document.createElement("div");
        aiRow.classList.add("row");
        newSessionBorder.appendChild(aiRow);

        var aiRowLabelCol = document.createElement("div");
        aiRowLabelCol.classList.add("col-3");
        aiRow.appendChild(aiRowLabelCol);

        var aiFormCheck = document.createElement("div");
        aiFormCheck.classList.add("form-check");
        aiRowLabelCol.appendChild(aiFormCheck);

        var aiCheckInput = document.createElement("input");
        aiCheckInput.classList.add("form-check-input");
        aiCheckInput.classList.add("new-session-ai");
        aiCheckInput.id = "session-ai-" + newSessionIndex;
        aiCheckInput.type = "checkbox"

        var aiElement = document.getElementById("session-ai-new");
        aiCheckInput.checked = aiElement.checked;
        aiFormCheck.appendChild(aiCheckInput);

        var aiCheckLabel = document.createElement("label");
        aiCheckLabel.classList.add("form-check-label");
        aiCheckLabel.htmlFor = "session-ai-" + newSessionIndex;
        aiCheckLabel.innerHTML = "allow AI"
        aiFormCheck.appendChild(aiCheckLabel);

        //new Structure
        var structureRow = document.createElement("div");
        structureRow.classList.add("row");
        newSessionBorder.appendChild(structureRow);

        var structureRowLabelCol = document.createElement("div");
        structureRowLabelCol.classList.add("col-3");
        structureRow.appendChild(structureRowLabelCol);

        var structureRowLabel = document.createElement("label");
        structureRowLabel.htmlFor = "select-structure-" + newSessionIndex;
        structureRowLabel.innerHTML = "Structure"
        structureRowLabelCol.appendChild(structureRowLabel);

        var structureRowSelectCol = document.createElement("div");
        structureRowSelectCol.classList.add("col-9");
        structureRow.appendChild(structureRowSelectCol);

        var structureRowSelect = document.createElement("select");
        structureRowSelect.classList.add("form-control");
        structureRowSelect.classList.add("new-session-structure");
        structureRowSelect.id = "select-structure-" + newSessionIndex;
        //TODO: get correct list of structures to replace this
        var structureRowSelectTemp = document.createElement("option");
        structureRowSelectTemp.value = sessionStructureIdNew;
        structureRowSelectTempText = $("#select-structure-new option:selected").text();
        structureRowSelectTemp.text = structureRowSelectTempText;
        structureRowSelect.appendChild(structureRowSelectTemp);
        //------
        structureRowSelectCol.appendChild(structureRowSelect);

        //new Market
        var marketRow = document.createElement("div");
        marketRow.classList.add("row");
        newSessionBorder.appendChild(marketRow);

        var marketRowLabelCol = document.createElement("div");
        marketRowLabelCol.classList.add("col-3");
        marketRow.appendChild(marketRowLabelCol);

        var marketRowLabel = document.createElement("label");
        marketRowLabel.htmlFor = "select-market-" + newSessionIndex;
        marketRowLabel.innerHTML = "Market"
        marketRowLabelCol.appendChild(marketRowLabel);

        var marketRowSelectCol = document.createElement("div");
        marketRowSelectCol.classList.add("col-9");
        marketRow.appendChild(marketRowSelectCol);

        var marketRowSelect = document.createElement("select");
        marketRowSelect.classList.add("form-control");
        marketRowSelect.classList.add("new-session-market");
        marketRowSelect.id = "select-market-" + newSessionIndex;
        //TODO: get correct list of markets to replace this
        var marketRowSelectTemp = document.createElement("option");
        marketRowSelectTemp.value = sessionMarketIdNew;
        marketRowSelectTempText = $("#select-market-new option:selected").text();
        marketRowSelectTemp.text = marketRowSelectTempText;
        marketRowSelect.appendChild(marketRowSelectTemp);
        //------
        marketRowSelectCol.appendChild(marketRowSelect);

        //
        sessionList.appendChild(newSession);

        //
        var sessionNameNewElement = document.getElementById("session-name-new");
        sessionNameNewElement.value = "";
        sessionNameNewElement.placeholder = "Enter Session Name";

        //already have this from above
        //var aiElement = document.getElementById("session-ai-new");
        aiElement.checked = true;

        var selectStructureElement = document.getElementById("select-structure-new");
        selectStructureElement.selectedIndex = 0;

        var selectMarketElement = document.getElementById("select-market-new");
        selectMarketElement.selectedIndex = 0;
    });

    $('#create_session_button').on('click', function () {
        var newSessions = document.querySelectorAll('.new-session');
        var numNewSessions = newSessions.length;
        if(numNewSessions < 1) {
            alert("Please create at least one new session");
            return;
        }

        sessionNameNew = $("#session-name-new").val();
        if(sessionNameNew) {
            var keepGoing = confirm("A new session may have not been added via the + button.\nContinue anyway?");
            if(!keepGoing) {
                return;
            }
        }

        teamId = $("#select-session-team option:selected").val();

        var newSessionList = [];
        for (i = 0; i < newSessions.length; ++i) {
            newSessionList.push(new Object());
        };

        var newSessionNames = document.querySelectorAll('.new-session-name');
        for (i = 0; i < newSessionNames.length; ++i) {
            let name = newSessionNames[i].value;
            if(name) {
                newSessionList[i].name = name;
            } else {
                let index = i + 1;
                alert("New session " + index + " does not have a name");
                return;
            }
        }

        var newSessionAI = document.querySelectorAll('.new-session-ai');
        for (i = 0; i < newSessionAI.length; ++i) {
            newSessionList[i].ai = newSessionAI[i].checked;
        }

        var newSessionStructures = document.querySelectorAll('.new-session-structure');
        for (i = 0; i < newSessionStructures.length; ++i) {
            newSessionList[i].structure = newSessionStructures[i].value;
        }

        var newSessionMarkets = document.querySelectorAll('.new-session-market');
        for (i = 0; i < newSessionMarkets.length; ++i) {
            newSessionList[i].market = newSessionMarkets[i].value;
        }

        createAjaxUrl = ajaxUrl + "create_session_group/"
        $.ajax({
            url: createAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
                teamId: teamId,
                newSessionList: JSON.stringify(newSessionList)
            },
            error: function (result) {
                //TODO: error message
                alert("New session creation failed");
            },
            success: function (result) {
                //clear new sessions
                //$('#create-session-modal').modal('hide');
                location.reload();                 
            }
        });
    });    
});
