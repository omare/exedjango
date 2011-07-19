jQuery(document).ready(function() {
	$(".toggle_feedback").live("click", function(e){
		$(this).next(".feedback").toggle();
		return false;
	});
	}
	);
