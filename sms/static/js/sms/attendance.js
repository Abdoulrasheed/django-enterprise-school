// $(document).ready(function(){
//     // present / absent
//     $("#materialChecked2").change(function(){
//         var isChecked = $('#materialChecked2').prop('checked');
//         if (isChecked){
//             $('#labelMaterialChecked2').text('Present');
//             $('#is_late').removeAttr('disabled');
//         }else{
//             $('#labelMaterialChecked2').text('Absent');
//             $('#is_late').removeAttr('checked');
//             $('#is_late').attr('disabled', 'disabled');
//         }
//     });

//     // late coming
//     $("#is_late").change(function(){
//         var isChecked = $('#is_late').prop('checked');
//         if (isChecked){
//             console.log("checked")
//             $('#late_coming').removeAttr('hidden');
//         }else{
//             $('#late_coming').attr('hidden', 'hidden');
//         }
//     });
// });

$(document).ready(function(){
    // present / absent
    $(".form-check-input").change(function(){
        var row = $(this).closest("form > tr");
        var isChecked = $(this).prop('checked');
        if (isChecked){
            row.find(".form-check-label").text('Present');
            row.find(".is_late").removeAttr('disabled');
        }else{
            row.find(".form-check-label").text('Absent');
            row.find(".is_late").prop('checked');
            row.find(".is_late").attr('disabled', 'disabled');
            row.find(".late_coming").attr('hidden', 'hidden');
        }
    });

    // late coming
    $(".is_late").change(function() {
        var row = $(this).closest("tr");
        var isChecked = $(this).prop('checked');
        if (isChecked){
            console.log("checked")
            row.find(".late_coming").removeAttr('hidden');
        }else{
            row.find(".late_coming").attr('hidden', 'hidden');
        }
    });
});