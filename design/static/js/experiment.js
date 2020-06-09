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
    if (hPort && (hPort !== "80" || hPort !== "443")) {
        ajaxUrl = location.protocol + "//" + location.hostname + ":" + hPort + "/exper/";
    }

    function getId(thiss) {
        thisId = $(thiss).attr('id');
        idSplit = thisId.split("_");
        idSplitId = idSplit[idSplit.length - 1];
        return idSplitId;
    }

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

    $('#create_session_button').on('click', function () {
        teamId = $("#select-session-team option:selected").val();
        session1Name = $("#session-1-name").val();
        session1AI = $("#session-1-ai").prop("checked");
        session1StructureId = $("#select-structure-1 option:selected").val();
        session1MarketId = $("#select-market-1 option:selected").val();
        create2nd = $("#second-session-check").prop("checked");
        session2Name = $("#session-2-name").val();
        session2AI = $("#session-2-ai").prop("checked");
        session2StructureId = $("#select-structure-2 option:selected").val();
        session2MarketId = $("#select-market-2 option:selected").val();
        createAjaxUrl = ajaxUrl + "create_session_group/";

        if(!session1Name) {
            alert("Please enter a name for Session 1");
            return;
        }
        if(create2nd && !session2Name) {
            alert("Please Enter a name for Session 2");
            return;
        }

        $('#session-1-name').val("");
        $("#session-1-ai").prop('checked', true);
        $("#session-1-ai").prop('disabled', false);
        $("#select-structure-1").val($("#select-structure-1 option:first").val());
        $("#select-market-1").val($("#select-market-1 option:first").val());
        $("#second-session-check").prop('checked', true);
        $('#session-2-name').prop('disabled', false);
        $('#session-2-name').val("");
        $("#session-2-ai").prop('checked', true);
        $("#session-2-ai").prop('disabled', false);
        $('#select-structure-2').prop('disabled', false);
        $("#select-structure-2").val($("#select-structure-2 option:first").val());
        $("#select-market-2").val($("#select-market-2 option:first").val());

        $('#create-session-modal').modal('hide');
        $.ajax({
            url: createAjaxUrl,
            method: "PUT",
            data: {
                csrfmiddlewaretoken: csrftoken,
                teamId: teamId,
                session1Name: session1Name,
                session1AI: session1AI,
                session1StructureId: session1StructureId,
                session1MarketId: session1MarketId,
                create2nd: create2nd,
                session2Name: session2Name,
                session2AI: session2AI,
                session2StructureId: session2StructureId,
                session2MarketId: session2MarketId
            },
            success: function (result) {
                location.reload();
            }
        });
    });

    $('#second-session-check').on('click', function () {
        if ($(this).prop("checked") == true) {
            $('#session-2-name').prop('disabled', false);
            $("#session-2-ai").prop('disabled', false);
            $('#select-structure-2').prop('disabled', false);
            $("#select-market-2").prop('disabled', false);
        } else {
            $('#session-2-name').prop('disabled', true);
            $("#session-2-ai").prop('disabled', true);
            $('#select-structure-2').prop('disabled', true);
            $("#select-market-2").prop('disabled', false);
        }
    });
});
