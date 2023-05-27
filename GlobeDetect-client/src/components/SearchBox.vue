<template>
	<div>
		<!-- Search Box -->
		<div class="container" @mouseover="expandBox" @mouseleave="foldBox">
			<input type="text" v-model="searchQuery" @keyup.enter="flyTo(searchResult[0])" @input="getSearchResult">
			<button @click="flyTo(searchResult[0])">
				<el-icon><Search /></el-icon>
			</button>
		</div>
	
		<!-- Candidate Box -->
		<ul class="candidate-box">
			<li v-if="searchResult.length === 0 && searchQuery !== ''" key="nothingMatch" class="py-1.5 px-5 relative z-50">
				No results match your query
			</li>
	
			<li v-for="result of searchResult" :key="result.id" @click="flyTo(result)" class="py-1.5 px-3 cursor-pointer relative z-50 
				whitespace-nowrap overflow-hidden text-ellipsis hover:bg-sky-600">
				{{ result.place_name }}
			</li>
		</ul>
	</div>
	
</template>

<script setup>
import { ref } from 'vue';
import axios from "axios";
import { ElContainer, ElMessage } from "element-plus"
import { useMapboxStore } from '@/stores/mapbox';
import { storeToRefs } from 'pinia';


const { map } = storeToRefs(useMapboxStore())
const mapboxAPIKey = 'pk.eyJ1IjoieHVlcnVveWFvIiwiYSI6ImNsYW05cjZ0dDA2dWEzdmxzajV3bmN4Z2YifQ.g_zwCEixkEiiiVaL20TsHQ'
const timerId = ref(0)
const searchQuery = ref('')
const searchResult = ref([])


function getSearchResult() {
	clearTimeout(timerId.value)
	timerId.value = setTimeout(() => {
		axios.get(`https://api.mapbox.com/geocoding/v5/mapbox.places/${searchQuery.value}.json?access_token=${mapboxAPIKey}&types=place`)
			.then((res) => {
				searchResult.value = res.data.features
			})
			.catch((err) => {
				ElMessage({
					message: 'Something goes wrong when searching, please turn to console for details',
					type: 'error',
					duration: 2000,
				})
				console.log(err)
			})
	}, 300)
}

function flyTo(result) {
	if(result) {
		map.value.fitBounds(result.bbox)
		searchQuery.value = ''
		searchResult.value = []
		foldBox()
	}
}

// Set the styles for search box expand and fold
function expandBox() {
	let container = document.querySelector('.container')
	container.style.width = '300px'
	container.style.border = '2px solid #409eff'
	container.style.backgroundColor = '#fff'
	container.style.opacity = '1'

	let searchInput = document.querySelector('.container input')
	searchInput.style.display = 'inline-block'
	searchInput.style.width = '220px'
}

function foldBox() {
	if(searchQuery.value == '') {
		let searchInput = document.querySelector('.container input')
		let container = document.querySelector('.container')
		container.style.width = '3.5rem'
		container.style.border = 'none'
		container.style.backgroundColor = '#409eff'
		container.style.opacity = '0.3'
		searchInput.style.width = '0px'
	}
}

</script>

<style scoped>
.container {
	width: 3.5rem;
	height: 3.5rem;
	border-radius: 70px;
	border: 2px solid transparent;
	background-color: #409eff;
	display: flex;
	align-items: center;
	justify-content: flex-end;
	transition: .8s;
	opacity: 0.3;
	overflow: hidden;
}
.container input {
	display: inline-block;
	width: 220px;
	padding: 0;
	font-size: 1.3rem;
	outline: none;
	border: none;
	background: transparent;
	transition: .8s;
}
.container button {
	border: none;
	padding: 10px 11.5px;
	margin-right: 5px;
	height: 2.9rem;
	width: 2.9rem;
	border-radius: 50%;
	background-color: #409eff;
	font: 900 1.5rem '';
	color: white;
}
.candidate-box {
	background-color: #409eff;
	width: 95%;
	left: 2.5%;
	top: 3.55rem;
	border-radius: 10px;
	font-size: 1.15rem;
	@apply absolute z-50 opacity-80 text-gray-200  shadow-xl;
}
</style>