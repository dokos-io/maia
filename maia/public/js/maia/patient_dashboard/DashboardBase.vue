<template>
	<div>
		<grid 
			:dashboardData="dashboardData"
			:isLoading="isLoading"
		/>
	</div>
</template>

<script>

import Grid from './Grid.vue';

export default {
	name: "DashboardBase",
	components: {
		Grid,
	},
	data() {
		return {
			dashboardData: {},
			patient_record: this.$root.patient_record,
			isLoading: false
		}
	},
	created() {
		maia.updates.on('refresh_dashboard', () => {
			this.getDashboardData();
		})
	},
	mounted() {
		this.getDashboardData()
	},
	methods: {
		getDashboardData() {
			this.isLoading = true;
			frappe.xcall('maia.maia.doctype.patient_record.dashboard.custom_patient_dashboard.get_data',
				{ patient_record: this.patient_record })
				.then(r => {
					this.dashboardData = r;
					this.isLoading = false;
					})
				.catch(() => this.isLoading = false)
		}
	}
}
</script>