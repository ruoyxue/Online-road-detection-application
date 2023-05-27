import { ref, computed } from 'vue'
import { defineStore } from 'pinia'


export const useMapboxStore = defineStore('mapbox', () => {
	let map = ref(null)
	let draw = ref(null)
	return { map, draw }
})