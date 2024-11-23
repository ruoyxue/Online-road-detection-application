<template>
	<ToolBar class="fixed top-20 left-6 z-10"/>
	<SearchBox class="fixed top-20 z-10" :style="{left: '20.2rem'}"/>
	<ProgressBar class="fixed left-6 bottom-6 z-30"/>
	
	<div id="map-viewer" class="h-full"></div>
</template>

<script setup>
import mapboxgl from 'mapbox-gl';
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import DrawRectangle from '@/composables/DrawRectangle.js'
import 'mapbox-gl/dist/mapbox-gl.css';
import '@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css';
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue';
import ToolBar from '@/components/ToolBar.vue';
import SearchBox from '@/components/SearchBox.vue';
import ProgressBar from '@/components/ProgressBar.vue';
import { useMapboxStore } from '@/stores/mapbox';
import { storeToRefs } from 'pinia';


const { map, draw } = storeToRefs(useMapboxStore())

onBeforeUnmount(() => {
	map.value = null
})

onMounted(() => {
	initMap()
})

function initMap() {
	mapboxgl.accessToken = 'pk.eyJ1IjoieHVlcnVveWFvIiwiYSI6ImNsYW05cjZ0dDA2dWEzdmxzajV3bmN4Z2YifQ.g_zwCEixkEiiiVaL20TsHQ'
	map.value = new mapboxgl.Map({
		container: 'map-viewer',
		style: 'mapbox://styles/mapbox/satellite-streets-v12',
		center: [102.3, 35.66],
		zoom: 1.5,
		projection: {
			name: 'globe'
		},
		antialias: false,
		maxZoom: 24,
		minZoom: 0,
  })

	map.value.on('style.load', () => {
    map.value.setFog({
        color: 'rgb(186, 210, 235)', // Lower atmosphere
        'high-color': 'rgb(36, 92, 223)', // Upper atmosphere
        'horizon-blend': 0.02, // Atmosphere thickness (default 0.2 at low zooms)
        'space-color': 'rgb(11, 11, 25)', // Background color
        'star-intensity': 0.6// Background star brightness (default 0.35 at low zoooms )
    })
	})

	// add draw tools
	let modes = MapboxDraw.modes;
	modes.draw_rectangle = DrawRectangle;
	draw.value = new MapboxDraw({
		modes: modes,
		displayControlsDefault: false,
	});
	map.value.addControl(draw.value);
	map.value.on('draw.create', function (e) {});
}

</script>

<style scoped>

:deep(.mapboxgl-ctrl-logo) {
	display: none;
}

</style>