$(document).on('click', '.menu-click-button', function() {
	$('.menu-click-button').attr('aria-expanded', 'false');
	if($(this).hasClass('collapsed')) {
		$(this).attr('aria-expanded', 'true');
	}
});


$(document).on('click', '.menu-click-button-menu', function() {
	if($(this).attr('aria-expanded') == 'false') {
		$(this).attr('aria-expanded', 'true');
	} else {
		$(this).attr('aria-expanded', 'false');
	}
});