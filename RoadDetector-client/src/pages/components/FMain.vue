<template>
	<div id="map-viewer"></div>
	<div id="geocoder-box"></div>

	<!-- step bar -->
	<el-steps :active="$store.state.detectionInfo.step" finish-status="success" process-status="finish" 
			direction="vertical" class="step-bar">
		<el-step title="Select Region" />
		<el-step :title="downloadString" />
		<el-step :title="detectionString" />
		<el-step title="Show Results" />
	</el-steps>

	<!-- LatLng Card -->
	<el-card id="latlon-info">
		<template #header>
			Longitude Latitude
		</template>
		{{ latlon }}
	</el-card>
</template>

<script setup>
import mapboxgl from 'mapbox-gl';
import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';
import MapboxLanguage from '@mapbox/mapbox-gl-language';
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import DrawRectangle from '~/composables/DrawRectangle'
import 'mapbox-gl/dist/mapbox-gl.css';
import '@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css';
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue';
import { useStore } from 'vuex';

const store = useStore()

let latlon = ref('')

let map, geocoder, draw

onBeforeUnmount(() => {
    map = null
});

onMounted(() => {
    init();
	document.getElementsByClassName("mapboxgl-ctrl-geocoder--input")[0].placeholder = "Location or Lng,Lat";
});


function init() {
	// create map
    mapboxgl.accessToken = 'pk.eyJ1IjoieHVlcnVveWFvIiwiYSI6ImNsYW05cjZ0dDA2dWEzdmxzajV3bmN4Z2YifQ.g_zwCEixkEiiiVaL20TsHQ'
    map = new mapboxgl.Map({
        container: 'map-viewer',
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: [102.3, 35.66],
        zoom: 2,
        projection: 'globe', // 为 3D 地球
        antialias: false,
		maxZoom: 24,
		minZoom: 0,
    });

	// add geocoder
	geocoder = new MapboxGeocoder({ 
		accessToken: mapboxgl.accessToken,
		localGeocoder: coordinatesGeocoder,
		language: 'en-US',
		flyTo: {
			bearing: 1,
			speed: 1, 
			curve: 1, 
		},
		mapboxgl: mapboxgl
	})
	document.getElementById('geocoder-box').appendChild(geocoder.onAdd(map));

	// add draw tools
	let modes = MapboxDraw.modes;
	modes.draw_rectangle = DrawRectangle;
	draw = new MapboxDraw({
		modes: modes,
		displayControlsDefault: false,
	});
	map.addControl(draw);
	map.on('draw.create', function (e) {});

	// language
	// map.addControl(new MapboxLanguage({ defaultLanguage: 'zh-Hans' }));
	// mapboxgl.setRTLTextPlugin('https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js');
	map.addControl(new MapboxLanguage({ defaultLanguage: 'en' }));
	
	map.on('mousemove', (e) => {
    	latlon.value = `( ${e.lngLat.lng.toFixed(4)}, ${e.lngLat.lat.toFixed(4)} )` 
	})

	store.commit('SET_Map', map)
	store.commit('SET_Draw', draw)

}

const coordinatesGeocoder = function (query) {
	// Match anything which looks like
	// decimal degrees coordinate pair.
	const matches = query.match(/^[ ]*(?:Lat: )?(-?\d+\.?\d*)[, ]+(?:Lng: )?(-?\d+\.?\d*)[ ]*$/i)
	if (!matches) {
		return null
	}
	
	function coordinateFeature(lng, lat) {
		return {
			center: [lng, lat],
			geometry: {
				type: 'Point',
				coordinates: [lng, lat]
			},
			place_name: 'Lat: ' + lat + ' Lng: ' + lng,
			place_type: ['coordinate'],
			properties: {},
			type: 'Feature'
		}
	}
	
	const coord1 = Number(matches[1])
	const coord2 = Number(matches[2])
	const geocodes = []
	
	if (coord1 < -90 || coord1 > 90) {
		// must be lng, lat
		geocodes.push(coordinateFeature(coord1, coord2))
	}
	
	if (coord2 < -90 || coord2 > 90) {
		// must be lat, lng
		geocodes.push(coordinateFeature(coord2, coord1))
	}
	
	if (geocodes.length === 0) {
		// else could be either lng, lat or lat, lng
		geocodes.push(coordinateFeature(coord1, coord2))
		geocodes.push(coordinateFeature(coord2, coord1))
	}
	
	return geocodes;
};

// step bar
let downloadString = computed(() => {
	let progress = store.state.detectionInfo.downloadCount / store.state.detectionInfo.sum
	let progressString = ''
	if (progress > 0 && progress < 1) {
		progressString = (progress * 100).toFixed(2) + '%'
	}
	return 'Download Images ' + progressString
})

let detectionString = computed(() => {
	let progress = store.state.detectionInfo.detectionCount / store.state.detectionInfo.sum
	let progressString = ''
	if (progress > 0 && progress < 1) {
		progressString = (progress * 100).toFixed(2) + '%'
	}
	return 'Road Detection ' + progressString
})


</script>


<style scoped>
#map-viewer { 
    top: 48px;
	bottom: 0px;
	left: 0px;
	right: 0px;
	z-index:-5;
	@apply fixed;
}

#geocoder-box {
	top: 100px;
	left: 40px;
	width: 350px;
	z-index: 100;
	pointer-events: none;
	@apply absolute flex justify-start;
}

.step-bar {
	position: absolute;
	left: 40px;
	width: 25%;
	height: 50%;
	top: 25%;
	z-index: 10;
	pointer-events: none;
}

#latlon-info {
	position: absolute;
	height: 70px;
	width: 200px;
	left: 40px;
	bottom: 35px;
	pointer-events: none;
	z-index: 100;
	@apply mt-auto text-stroke-sm text-light-500 bg-neutral-600 border-0;
}

:deep(.el-card__header) {
	@apply pt-2 pb-0 flex justify-center items-center border-0;
}

:deep(.el-card__body) {
	@apply pt-1.5 pb-1 px-0 flex justify-center items-center border-0;
}

:deep(.mapboxgl-ctrl-geocoder) {
	min-width: 100%;
}

:deep(.el-step__title) {
	font-size: 20px;
	font-weight: bold;
	@apply px-3 pt-1;
}

:deep(.el-step__icon) {
	height: 32px;
	width: 32px;
	font-size: 20px;
}

:deep(.el-step.is-vertical .el-step__line) {
	width: 5px;
	left: 14px;
	top: 3px;
	bottom: -3px;
}

:deep(.mapboxgl-ctrl-logo) {
    display: none;
}

</style>