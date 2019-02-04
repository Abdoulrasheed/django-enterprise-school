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
    });

    // late coming
    $("#is_late").change(function(){
        var isChecked = $('#is_late').prop('checked');
        if (isChecked){
            console.log("checked")
            $('#late_coming').removeAttr('hidden');
        }else{
            $('#late_coming').attr('hidden', 'hidden');
        }
    });
});