$(document).ready(function(){
    // present / absent
    $(".custom-checkbox").change(function(){
        var row = $(this).closest("tr > td");
        a = $(row).find("#goo").prop('checked');
        if(a == true){
            $(row).find(".custom-control-label").text('Present');
        }else{
            $(row).find(".custom-control-label").text('Absent');
        }

        var row2 = $(this).closest("tr");
        var isChecked = $(row).find('#goo').prop('checked');
        if (!isChecked){
            $(row2).find('#is_late').attr('disabled', 'disabled')
        }else{
            $(row2).find('#is_late').removeAttr('disabled')
        }

        $(row2).find("#is_late").change(function(){
        var row3 = $(this).closest("tr");
        check = $(row2).find("#is_late").prop('checked');
        if(!check){
            $(row2).find("#late_coming").attr('hidden','hidden');
        }else{
            $(row2).find("#late_coming").removeAttr('hidden');
        }
        });
    });

    var savebtn = $("#no_data").text()
    if(savebtn == ''){
        $("#saveAttendance").removeAttr("hidden")
    }
});