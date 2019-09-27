<template>
	<div class="content-container">
		<customer-account-details v-if="selected_section=='Account'"/>
		<customer-account-invoices v-if="selected_section=='Invoices'"/>
	</div>
</template>

<script>
import CustomerAccountDetails from "./CustomerAccountDetails.vue";
import CustomerAccountInvoices from "./CustomerAccountInvoices.vue";

export default {
	name: "CustomerAccount",
	components: {
		CustomerAccountDetails,
		CustomerAccountInvoices
	},
	data() {
		return {
			selected_section: null
		}
	},
	created() {
		dokos.customer_account_update.on("change", e => {
			this.selected_section = e.selected_section;
		})
	}
};
</script>

<style lang="less" scoped>
.layout-main-section {
	border: 0px;
}
</style>