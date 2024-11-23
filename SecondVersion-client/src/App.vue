<template>
	<header>
		<Navigation/>
	</header>
	<main>
		<router-view v-slot="{ Component, route }">
			<keep-alive include="MainView">
					<component :is="Component" :key="route.fullPath"/>
			</keep-alive>
		</router-view>
	</main>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Navigation from './components/Navigation.vue';



</script>

<style scoped>
header {
	height: 5vh;
	font-family: 'Roboto', sans-serif;
	@apply fixed top-0 left-0 z-10 bg-transparent w-full text-gray-100;
}

main {
	height: 100vh;
}

</style>
