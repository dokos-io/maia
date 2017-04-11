// Copyright (c) 2017, DOKOS and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('maia');

// add toolbar icon
$(document).bind('toolbar_setup', function() {
	frappe.app.name = "Maia";

	frappe.help_feedback_link = '<p><a class="text-muted" \
		href="https://dokos.io">Feedback</a></p>'

	$('.navbar-home').html('<img class="erpnext-icon" src="'+
			frappe.urllib.get_base_url()+'/assets/maia/images/maia_squirrel.svg" />');
	
	$('[data-link="docs"]').attr("href", "https://dokos.io/")
	$('[data-link="issues"]').attr("href", "https://dokos.io/")

        var $help_menu = $('.dropdown-help ul .documentation-links');
        $help_menu.prev().remove();
	$help_menu.prev().remove();
	$help_menu.prev().remove();

	$('<li><a data-link-type="forum" href="https://dokos.io" \
		target="_blank">'+__('User Forum')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="https://dokos.io" \
		target="_blank">'+__('Chat')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="https://dokos.io" \
		target="_blank">'+__('Report an Issue')+'</a></li>').insertBefore($help_menu);

});
