// Copyright (c) 2017, DOKOS and Contributors
// See license.txt

// add toolbar icon
$(document).bind('toolbar_setup', function() {
	frappe.app.name = "Maia";

	if (frappe.user.has_role("System Manager")) {
		let help_links = [];
		help_links.push(`<li class="usage-info-link"><a href="#maia-account">${__("Maia Account")}</a></li>`);
		$(help_links.join("\n")).insertBefore($("#toolbar-user").find("li:first"));
	}

	$('.navbar-home').html('<img class="maia-icon" src="'+
			frappe.urllib.get_base_url()+'/assets/maia/images/maia_squirrel.svg" />');

	$('[data-link="docs"]').attr("href", "https://doc.maia-by-dokos.fr")
	$('[data-link="issues"]').attr("href", "https://github.com/DOKOS-IO/maia/issues")

	var $help_menu = $('.dropdown-help ul .documentation-links');
	$help_menu.prev().remove();
	$help_menu.prev().remove();
	$help_menu.prev().remove();

	$('<li><a href="mailto:help@dokos.io" \
		target="">'+__('Report an Issue')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="https://doc.maia-by-dokos.fr" \
		target="_blank">'+__('Read the documentation')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="https://www.cnil.fr/fr/traitement-de-donnees-de-sante-comment-informer-les-personnes-concernees" \
		target="_blank">'+__('Affichette CNIL')+'</a></li>').insertBefore($help_menu);
	$('<li><a href="https://maia-by-dokos.fr/files/MODELE_DE_NOTE_D%E2%80%99INFORMATION_DES_USAGERS_RELATIVE_A_L%E2%80%99HEBERGEMENT_DE_DONNEES_DE_SANTE_A_CARACTERE_PERSONNEL.pdf" \
		target="_blank">'+__('Information Légale')+'</a></li>').insertBefore($help_menu);
});
