<template>
	<div class="home">
		<video class="bg-video" autoplay muted loop>
			<source src="../assets/home.mp4" type="video/mp4">
			Your brower is not supported!
		</video>
		<h2 class="home__title">Detect anywhere</h2>
		<h3 class="home__subtitle">Feel free to detect roads and buildings anywhere in real world</h3>
		<router-link class="home__button" to="/view">Start exploring</router-link>
	</div>
</template>

<script setup>
import { RouterLink } from 'vue-router';

</script>

<style scoped>
.home {
	height: 100%;
	
}

.bg-video {
	height: 100%;
	width: 100%;
	object-fit: cover;
}

.home__title {
	top: 25%;
	font-size: 100px;
	min-width: max-content;
	animation-name: moveInLeft;
	animation-duration: 1s;
	animation-timing-function: ease-out;
	@apply text-white uppercase font-bold absolute z-50 left-1/2 -translate-x-1/2;
}

.home__subtitle {
	top: 42%;
	font-size: 36px;
	min-width: max-content;
	animation: moveInRight 1s ease-out;
	@apply text-white font-thin absolute z-50 left-1/2 -translate-x-1/2;
}

.home__button {
	top: 62%;
	font-size: 30px;
	min-width: max-content;
	display: block;
	border-radius: 100px;
	transition: .2s ease-in-out;
	animation: moveInBottom 1s ease-out .75s;
	animation-fill-mode: backwards;
	@apply text-white uppercase absolute z-50 left-1/2 -translate-x-1/2
	bg-blue-500 py-4 px-10 hover:-translate-y-1 active:-translate-y-0.5;
}

@keyframes moveInLeft {
	0% {
		opacity: 0;
		transform: translateX(calc(-10rem - 50% ));
	}

	80% {
		transform: translateX(calc(1rem - 50% ));
	}

	100% {
		opacity: 1;
		transform: translateX(-50%);
	}
}

@keyframes moveInRight {
	0% {
		opacity: 0;
		transform: translateX(calc(10rem - 50% ));
	}

	80% {
		transform: translateX(calc(-1rem - 50% ));
	}

	100% {
		opacity: 1;
		transform: translateX(-50%);
	}
}

@keyframes moveInBottom {
	0% {
		opacity: 0;
		transform: translate(-50%, 2rem);
	}
	70% {
		transform: translate(-50%, -.2rem);
	}

	100% {
		opacity: 1;
		transform: translateX(-50%);
	}
}



</style>