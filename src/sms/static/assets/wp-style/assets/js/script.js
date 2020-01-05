(function($) {
	// 'use strict';

	// $("#write-content").jqte();

	$(".add--media").on("click", function(e) {
		e.preventDefault();
		$("body").addClass("show--media");
	});

	$(".overlay, .btn-close").on("click", function() {
		$("body").removeClass("show--media");
	});

	$("#set-featured-img").on("click", function() {
		$("body").addClass("show--media");
		$(".media-sidebar ul li, #insert-media, .upload--menu ul li").removeClass("active");
		$(".media-sidebar ul li.f-image-active, #featured-image, .upload--menu ul li.f-media-active, #upload-media-library6").addClass("active");
	});

	$(".overlay, .btn-close, #set-f-img").on("click", function() {
		$(".media-sidebar ul li, #insert-media, .upload--menu ul li").addClass("active");
		$(".media-sidebar ul li.f-image-active, #featured-image, .upload--menu ul li.f-media-active, #upload-media-library6").removeClass("active");
	});



	//draft
	$(".post-status-select").hide();
	// $(".draft-edit").on("click", function(e) {
	// 	e.preventDefault();
	// 	$(".draft-show").show(250);
	// 	$(this).hide();
	// });

	// $(".cancel-post-status").on("click", function(e) {
	// 	e.preventDefault();
	// 	$(".draft-show").hide(250);
	// 	$(".draft-edit").show();
	// });

	// //visibility 
	// $(".visibility-edit").on("click", function(e) {
	// 	e.preventDefault();
	// 	$(".visibility-status-select").show(250);
	// 	$(this).hide();
	// });

	// $(".cancel-post-status").on("click", function() {
	// 	$(".visibility-status-select").hide(250);
	// 	$(".visibility-edit").show();
	// });

	// //publish
	// $(".publish-edit").on("click", function() {
	// 	$(".publish-status-select").show(250);
	// 	$(this).hide();
	// });

	// $(".cancel-post-status").on("click", function() {
	// 	$(".publish-status-select").hide(250);
	// 	$(".publish-edit").show();
	// });

	$('.post-edit').click(function(e) {
		e.preventDefault();
		var id = $(this).attr('id');
		$('#'+id +'-show').show();
		$('#' + id).hide();
		console.log(id);
	});

	$('.cancel-post-status').click(function(e) {
		e.preventDefault();
		// var id = $(this).attr('id');
		$(this).parent().hide();
		var getClass = $(this).parent().parent().attr('class');
		console.log(getClass);
		// var lastClass = ('.' + getClass +':nth-last-child');
		var showElement = $('.' + getClass +':last-child()').find('a').attr('id');
		// $('.' + getClass +':nth-last-child()').show();
		// console.log($(this).parent().parent(0).attr('class'));
		console.log(showElement);
		

	})


}(jQuery));