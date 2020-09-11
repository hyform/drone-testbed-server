$(document).ready(function () {
    var ajaxUrl = getAjaxUrl("exper");

    $('#select-organization').on('change', function () {
        $("#select-study").empty();
        selectAjaxUrl = ajaxUrl + "select_organization/"
        var orgId = $("#select-organization option:selected").val();
        if(orgId) {
            $.ajax({
                url: selectAjaxUrl,
                method: "PUT",
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    orgId: orgId
                },
                success: function (result) {                    
                    $('#select-study').append($("<option></option>"));
                    var studies = JSON.parse(result);
                    for (const [key, value] of Object.entries(studies)) {
                        $('#select-study').append($("<option></option>").attr("value", value).text(key));
                    }
                }
            });
        }
    });

    $('#select-study').on('change', function () {
        $("#select-experiment").empty();
        selectAjaxUrl = ajaxUrl + "select_study/"
        var studyId = $("#select-study option:selected").val();
        if(studyId) {
            $.ajax({
                url: selectAjaxUrl,
                method: "PUT",
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    studyId: studyId
                },
                success: function (result) {                    
                    $('#select-experiment').append($("<option></option>"));
                    var experiments = JSON.parse(result); 
                    for (const [key, value] of Object.entries(experiments)) {
                        $('#select-experiment').append($("<option></option>").attr("value", value).text(key));
                    }
                }
            });
        }
    });

    $('#continue_button').on('click', function () {
        selectAjaxUrl = ajaxUrl + "continue_to_experiment/"
        var orgId = $("#select-organization option:selected").val();
        var studyId = $("#select-study option:selected").val();
        var expId = $("#select-experiment option:selected").val();
        if(orgId && studyId && expId) {
            $.ajax({
                url: selectAjaxUrl,
                method: "PUT",
                data: {
                    csrfmiddlewaretoken: csrftoken,
                    orgId: orgId,
                    studyId: studyId,
                    expId: expId
                },
                success: function (result) {
                    window.location.href = "/experiment";
                }
            });
        } else {
            alert("Please select an Organization, Study, and Experiment")
        }
    });
})