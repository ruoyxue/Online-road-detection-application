<template>
	<div class="navigation-bar">
		<span class="title">EarthVision and Application</span>
		<div class="navigation-tabs">
			<router-link to="/" id="home-tab">Home</router-link>
			<router-link to="/view" id="view-tab">View</router-link>
			<a href="https://www.baidu.com/" target="_blank" id="team-tab">Team</a>
			<a href="https://github.com/ruoyxue" target="_blank" id="developer-tab">Developer</a>
			<div class="underline-bar"></div>
		</div>
		
	</div>
</template>

<script setup>
import { RouterLink } from 'vue-router'

</script>

<style scoped>
.navigation-bar {
	display: grid;
	grid-template-columns: 1fr max-content;
	font-size: 1.4rem;
	@apply py-5 px-8 font-normal text-gray-100;
}

.title {
	font-size: 1.7rem;
	@apply italic font-bold;
}

.navigation-tabs {
	display: grid;
	grid-template-columns: repeat(4, max-content);
	grid-column-gap: 2rem;
	position: relative;
}

.underline-bar {
	position: absolute;
	bottom: 0;
	left: 0;
	width: 0;
	height: 4px;
	border-radius: 2px;
	transition: .5s;
}

#home-tab:hover ~ .underline-bar{
	left: 0;
	background-color: rgb(250, 190, 250);
	width: 61px;
}
#view-tab:hover ~ .underline-bar{
	left: 90px;
	background-color: red;
	width: 53px;
}
#team-tab:hover ~ .underline-bar{
	left: 172px;
	background-color: #d18df8;
	width: 58px;
}
#developer-tab:hover ~ .underline-bar{
	left: 260px;
	background-color: #ffb1b1;
	width: 100px;
}

</style>