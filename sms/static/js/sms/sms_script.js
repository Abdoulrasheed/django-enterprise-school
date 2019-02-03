$(document).ready(function(){
	$("#select_class").change(function(){
			var value= $('#select_class option:selected').attr('value');
			action_column = '<a title="view" class="blue-text"><i class="fa fa-user"></i></a>\
                			<a title="edit" class="teal-text"><i class="fa fa-pen"></i></a>\
                			<a title="delete" class="red-text"><i class="fa fa-times"></i></a>'

			$.ajax({
            	method: "GET",
            	url: '/students/' + value,
            	success: function(data) {
               	    var table = $("#table tbody");
               	    var picture_url = window.location.protocol+"//"+window.location.host+data.students[1]
               	    if(data.students[0] != undefined){
               	    	table.html("")
               	    	$('#no_data').text("")
            ,   	    	if(data.students[4] == true){
               	    		status_column = '<span class="switch"><label><input type="checkbox" checked>\
								<span class="lever"></span>\
								</label></span>'
						}else{
							status_column = '<span class="switch"><label><input type="checkbox">\
								<span class="lever"></span>\
								</label></span>'
						}
        				table.append("<tr>\
        					<td>"+data.students[0]+"</td>\
        					<td>"+"<img width='35px' src="+picture_url+"></td>\
        					<td>"+data.students[2]+"</td>\
        					<td>"+data.students[3]+"</td>\
        					<td>"+status_column+"</td>\
        					<td>"+action_column+"</td>");
               	    }else{
               	    	table.html("")
               	    	$('#no_data').text("")
               	    	$('#no_data').text('No student available for selected class');
               	    }
            },
            error: function(error_data) {
                console.log(error_data)
            },
        })
	});
});