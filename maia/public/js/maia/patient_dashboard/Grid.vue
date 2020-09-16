<template>
	<div class="card-columns">
		<div
			v-if="isLoading"
			class="loading text-muted small">
			{{ __("Loading...") }}
		</div>

		<dashboard-card
			v-for="item in enabledDashboardData"
			:key="item"
			:itemName="item"
			:dashboardData="dashboardData"
			class="card"
		/>
	</div>
</template>

<script>

import DashboardCard from './DashboardCard.vue';

export default {
	name: "Grid",
	components: {
		DashboardCard
	},
	props: ["dashboardData", "isLoading"],
	data() {
		return {
		}
	},
	computed: {
		enabledDashboardData: function() {
			return Object.keys(this.dashboardData).filter(key => this.dashboardData[key]["enabled"] === 1);
		}
	},
	mounted() {
	},
	methods: {
	}
}
</script>

<style lang="scss">
@import "./../../../scss/mixins.scss";

.grid {
	padding-bottom: 10px;
	@include grid-6(&);
	.widget {
		width: auto;
		justify-content: center;
		align-items: center;
		text-align: center;
		flex-basis: auto;
		margin: 10px 1% 0 1%;
		width:  calc(25% - 2%);
		min-height: 75px;
		background: #303030;
	}
	.loading {
		width: 100%;
		min-height: 120px;
		display: flex;
		justify-content: center;
		align-items: center;
	}
}
</style>