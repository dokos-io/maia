<template>
	<div class="frappe-list">
		<div  v-if="invoices.length != 0" class="result">
			<div class="list-headers">
				<header class="level list-row list-row-head text-muted small">
					<div class="level-left list-header-subject">
						<div class="list-row-col ellipsis level hidden-xs">
							<span class="level-item">{{ columns[0].label }}</span>
						</div>
						<div class="list-row-col ellipsis"  v-for="(column, index) in columns.slice(1)" :key="index" :class="{'text-right': column.right}">
							<span>{{ column.label }}</span>
						</div>
					</div>
					<div class="level-right">
						<span class="list-count"></span>
					</div>
				</header>

			</div>
			<div class="result-list">
				<div class="list-row-container" v-for="(d, index) in invoices" :key="index">
					<div class="level list-row small">
						<div class="level-left ellipsis">
							<div class="list-row-col ellipsis level hidden-xs">
								<span class="level-item bold" :title="d[columns[0].fieldname]">
									{{ d[columns[0].fieldname] }}
								</span>
							</div>
							<div class="list-row-col ellipsis" v-for="(column, index) in columns.slice(1)" :key="index" :class="{'text-right': column.right}">
								<span class="ellipsis text-muted">{{ d[column.fieldname] }}</span>
							</div>
						</div>
						<div class="level-right ellipsis">
							<div class="list-row-col ellipsis level">
								<span class="level-item ellipsis text-muted">
									<a class="btn btn-xs btn-default" :href="d['print_link']" target="_blank">{{ __("Print") }}</a>
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div v-else class="result no-invoices">
			<div class="no-invoices-text">
				<h4 class="text-muted">{{ __("No invoices") }}</h4>
			</div>
		</div>
		<div v-if="invoices.length != 0&&more" class="more-block">
			<button class="btn btn-light btn-more btn-sm" @click="get_invoices">{{ __("More") }}</button>
		</div>
	</div>
</template>

<script>
export default {
	name: "CustomerAccountInvoices",
	data() {
		return {
			request: [],
			columns: [
				{label: __("Name"), fieldname: "name"},
				{label: __("Date"), fieldname: "formatted_date"},
				{label: __("Amount"), fieldname: "formatted_grand_total"},
			],
			options: {
				start: 0,
				length: 20,
				order_by: "posting_date desc"
			},
			more: true
		}
	},
	mounted() {
		this.get_invoices();
	},
	computed: {
		invoices: function() {
			moment.locale(frappe.boot.lang || 'en');
			this.request.forEach(value => {
				value["formatted_grand_total"] = format_currency(value["grand_total"], value["currency"]);
				value["formatted_date"] = frappe.datetime.global_date_format(value["posting_date"]);
			})

			return this.request
		},
	},
	methods: {
		get_invoices: function() {
			frappe.xcall("maia.maia.page.maia_account.maia_account.get_invoices", {options: this.options})
			.then(e => {
				if (e && e.message) {
					this.request = [...this.request, ...e.message]
					this.options.start = this.options.start + this.options.length;
					this.more = e.message.length < this.options.length ? false : true;
				};
			})
		}
	}
};

</script>

<style lang="less" scoped>
.more-block {
	width: 80%;
	margin-top: 20px;
}

.btn-more {
	float: right;
}

.no-invoices {
	display: flex;
	justify-content: space-around;
	.no-invoices-text {
		margin-top: auto;
		margin-bottom: auto;
	}
}

</style>