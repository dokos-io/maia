<template>
	<div class="dokos-customer-account">
		<div class="row padded-row">
			<div class="col-lg-4">
				<h3>{{ __("My billing address") }}</h3>
			</div>
			<div class="col-lg-8">
				<h4 class="customer-name">{{ customer_name }}</h4>
				<div v-if="billing_addresses.length">
					<div v-for="(address, index) in billing_addresses" :key="index">
						<div><span v-html="address.display"></span></div>
						<div class="edit-address"><a class="btn btn-xs btn-primary" @click="edit_address(address)">{{ __("Edit") }}</a></div>
					</div>
				</div>
				<div v-else>
					<div><a class="btn btn-xs btn-primary" @click="new_address">{{ __("Add a billing address") }}</a></div>
				</div>
			</div>
		</div>
		<hr>
		<div class="row padded-row">
			<div class="col-lg-4">
				<h3>{{ __("My payment methods") }}</h3>
			</div>
			<div class="col-lg-8">
				<div class="profile-card" v-for="details in billing_details.data" :key="details.id">
					<div class="row">
						<div class="col-12 col-sm-9 col-md-10">
							<h4>{{ details.card.brand }}</h4>
							<h5>{{ details.card.name }} xxxxx-{{ details.card.last4 }}</h5>
							<p>{{ __("Expires") }} {{ details.card.exp_month }}/{{ details.card.exp_year }}</p>
						</div>
						<div class="col-12 col-sm-3 col-md-2">
							<button class="btn btn-close" @click="remove_card(details.id)">
								<i class="fas fa-times"></i>
							</button>
						</div>
					</div>
				</div>
				<div v-if="!show_new_card"><a class="btn btn-xs btn-primary" @click="new_card">{{ __("Add a new payment card") }}</a></div>
				<div v-else class="profile-card">
					<div ref="card"></div>
				</div>
				<div v-if="show_new_card">
					<a class="btn btn-xs btn-primary btn-new-card" @click="create_new_card">{{ __("Add this card") }}</a>
					<a class="btn btn-xs btn-default btn-new-card" @click="cancel_new_card">{{ __("Cancel") }}</a>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { AddressDialog } from './address_dialog.js';
export default {
	name: "CustomerAccountDetails",
	data() {
		return {
			customer_name: null,
			billing_addresses: [],
			billing_details: [],
			show_new_card: false,
			public_key: null,
			stripe: null,
			card: null
		}
	},
	mounted() {
		this.get_account_details();
		this.get_customer_payment_methods();
		this.get_stripe_pub_key();
	},
	methods: {
		get_account_details: function() {
			frappe.xcall("maia.maia.page.maia_account.maia_account.get_account_details")
			.then(e => {
				if (e && e.message) {
					this.customer_name = e.message.customer_name;
					this.billing_addresses = e.message.billing_addresses;
				};
			})
		},
		edit_address: function(address) {
			const me = this;
			this.address_dialog = AddressDialog(__("Edit address"), {
				label: __("Update"),
				on_submit: function(data) {
					me.update_address(data)
				},
				data: address
			})
			this.address_dialog.show()
		},
		update_address: function(data) {
			const {name, ...filtered_data} = data;
			const address_data = { ...filtered_data, address_title: this.customer_name };
			frappe.xcall('maia.maia.page.maia_account.maia_account.update_address', {data: filtered_data, name: name})
			.then(e => {
				this.address_dialog.hide();
				this.get_account_details();
			})
		},
		new_address: function() {
			const me = this;
			this.address_dialog = AddressDialog(__("New address"), {
				label: __("Add"),
				on_submit: function(data) {
					me.add_address(data)
				}
			})
			this.address_dialog.show()
		},
		add_address: function(data) {
			frappe.xcall('maia.maia.page.maia_account.maia_account.add_address', {data: data, customer: this.customer_name})
			.then(e => {
				this.address_dialog.hide();
				this.get_account_details();
			})
		},
		get_customer_payment_methods: function(data) {
			frappe.xcall('maia.maia.page.maia_account.maia_account.get_customer_payment_methods')
			.then(e => {
				if (e && e.message) {
					this.billing_details = e.message;
				}
			})
		},
		remove_card: function(data) {
			frappe.xcall('maia.maia.page.maia_account.maia_account.remove_card', {card: data})
			.then(e => {
				if (e) {
					this.get_customer_payment_methods()
				}
			})
		},
		new_card: function(data) {
			this.show_new_card = true;
			Vue.nextTick()
			.then(() => {
				this.stripe = Stripe(this.public_key);
				let style = {
					base: {
						border: '1px solid #D8D8D8',
						borderRadius: '4px',
						color: "#000",
					},

					invalid: {
						// All of the error styles go inside of here.
					}

				};
				this.card = this.stripe.elements().create('card', style);
				this.card.mount(this.$refs.card);
			})
		},
		create_new_card: function() {
			const me = this;
			this.stripe.createToken(this.card).then((result) => {
				if (result.error) {
					me.hasCardErrors = true;
					me.$forceUpdate(); // Forcing the DOM to update so the Stripe Element can update.
					return;
				} else {
					return frappe.xcall('maia.maia.page.maia_account.maia_account.create_new_card', {token: result});
				}
			}).then(r => {
				this.show_new_card = false;
				this.get_customer_payment_methods()
			})
		},
		cancel_new_card: function() {
			this.show_new_card = false;
		},
		get_stripe_pub_key: function() {
			frappe.xcall('maia.maia.page.maia_account.maia_account.get_stripe_public_key')
			.then(e => {
				if (e && e.message) {
					this.public_key = e.message;
				}
			})
		}
	}
};

</script>

<style lang="less" scoped>
.edit-address {
	margin-top: 2px;
	float: right;
}

.dokos-customer-account {
	.customer-name {
		margin-top: 20px;
	}

	.btn-close,
	.btn-new-card {
		float: right;
	}

	.btn-new-card {
		margin-left: 5px;
	}
}

.profile-card {
	border: 1px solid #EEE;
	border-radius: 3px;
	background-color: #FFF;
	margin: 0px 0px 15px 0px;
	padding: 20px;
}

.padded-row {
	padding: 15px;
}
</style>