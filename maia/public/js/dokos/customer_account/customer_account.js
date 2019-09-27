import CustomerAccount from "./CustomerAccount.vue";

maia.DokosCustomerAccount = class DokosCustomerAccount {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("Maia account"),
			single_column: false
		});

		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(`<ul class="module-sidebar-nav overlay-sidebar nav nav-pills nav-stacked"></ul>`);
		this.$sidebar_list = this.page.sidebar.find('ul');

		this.stripeURL = "https://js.stripe.com/v3/"

		// const list of doctypes
		this.sections = [{"name": "Account", "label": __("Account"), "icon": "fa fa-address-book-o"}, {"name": "Invoices", "label": __("Invoices"),"icon": "fa fa-file-text-o"}];

		// for saving current selected filters
		// TODO: revert to 0 index for doctype and timespan, and remove preset down
		const _initial_section = this.sections[0].name;

		this.options = {
			selected_section: _initial_section
		};

		this.message = null;
		this.validate_account()
	}

	validate_account() {
		frappe.xcall('maia.maia.page.maia_account.maia_account.validate_account')
		.then(r => {
			if (r === true) {
				this.make();
				this.load_stripe();
			} else {
				this.make_error_container();
			}
		})
	}

	make_error_container() {
		$(`<div class="page-main-content">
			<div style="text-align: center; padding: 250px;" class="text-muted">${__("Your account could not be found. Please contact the support.")}</div>
		</div>`).appendTo(this.page.main);
	}

	make() {
		const me = this;

		const $container = $(`<div class="leaderboard page-main-content">
			<div class="leaderboard-list"></div>
		</div>`).appendTo(this.page.main);


		this.sections.map(section => {
			this.get_sidebar_item(section).appendTo(this.$sidebar_list);
		});

		this.$sidebar_list.on('click', 'li', function(e) {
			let $li = $(this);
			let section = $li.find('span').attr("section-value");

			me.options.selected_section = section;

			me.$sidebar_list.find('li').removeClass('active');
			$li.addClass('active');

			dokos.customer_account_update.trigger("change", me.options);

		});
		me.get_content($container);

		// now get leaderboard
		this.$sidebar_list.find('li:first').trigger('click');
	}

	get_content($container) {
		new Vue({
			el: $container[0],
			render: h => h(CustomerAccount),
			data: {
				'page': this.page
			}
		});
	}


	get_sidebar_item(item) {
		return $(`<li class="strong module-sidebar-item">
			<a class="module-link">
			<i class='${item.icon}' aria-hidden="true"></i>
			<span style="margin-left: 15px;" section-value="${item.name}">${item.label}</span></a>
		</li>`);
	}

	load_stripe() {
		const me = this;
		return new Promise(function (resolve, reject) {
			if (document.querySelector('script[src="' + me.stripeURL + '"]')) {
				resolve();
				return;
			}
			const el = document.createElement('script');
			el.type = 'text/javascript';
			el.async = true;
			el.src = me.stripeURL;
			el.addEventListener('load', resolve);
			el.addEventListener('error', reject);
			el.addEventListener('abort', reject);
			document.head.appendChild(el);
		});
	}
}

frappe.provide('dokos.customer_account_update')
frappe.utils.make_event_emitter(dokos.customer_account_update);