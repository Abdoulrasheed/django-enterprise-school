$(document).ready(function(){
	$("#select_class").change(function(){
			var value= $('#select_class option:selected').attr('value');
			$.ajax({
            	method: "GET",
            	url: '/students/' + value,
            	success: function(data) {
               	    var table = $("#table tbody");
               	    var picture_url = window.location.protocol+"//"+window.location.host+data.students[1]
               	    if(data.students[0] != undefined){
               	    	table.html("")
               	    	$('#no_data').text("")
        				table.append("<tr><td>"+data.students[0]+"</td><td>"+"<img width='30px' src="+picture_url+"></td><td>"+data.students[2]+"</td><td>"+data.students[3]+"</td> <td>"+data.students[4]+"</td> <td>"+data.students[5]+"</td>");
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