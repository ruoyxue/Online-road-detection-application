<template>
<el-drawer v-model="showSettingDrawer" size="25%" :show-close="false">
	<template #header>
		<span class="drawer-title">
			<el-icon><Setting/></el-icon>
			<span class="px-3">Settings</span>
		</span>
	</template>

	<el-collapse class="settingBody">
		<!-- MapBox Style -->
		<el-collapse-item title="MapBox Style" name="Map Style">
			<span class="single-drawer-item">
				Country Label Language
				<el-select v-model="language" class="select" size="default" @change="changeLanguage">
					<el-option key="English" label="English" value="en"/>
					<el-option key="Chinese" label="Chinese" value="zh-Hans"/>
					<el-option key="French" label="French" value="fr"/>
					<el-option key="German" label="German" value="de"/>
					<el-option key="Russian" label="Russian" value="ru"/>
					<el-option key="Spanish" label="Spanish" value="es"/>
				</el-select>
			</span>
			<el-divider />

			<span class="single-drawer-item">
				Projection
				<el-select v-model="projection" class="select" size="default" @change="changeMapProjection">
					<el-option key="globe" value="globe"/>
					<el-option key="mercator" value="mercator"/>
					<el-option key="albers" value="albers"/>
					<el-option key="winkelTripel" value="winkelTripel"/>
					<el-option key="equirectangular" value="equirectangular"/>
					<el-option key="LCC" label="LCC" value="lambertConformalConic"/>
				</el-select>
			</span>
			<el-divider />

			<span class="single-drawer-item">
				Map Style
				<el-select v-model="style" class="select" size="default" @change="changeMapStyle">
					<el-option key="satellite" value="satellite"/>
					<el-option key="satellite street" value="satellite street"/>
					<el-option key="streets" value="streets"/>
					<el-option key="light" value="light"/>
					<el-option key="dark" value="dark"/>
				</el-select>
			</span>
			<el-divider />

			<span class="single-drawer-item">
				World View
				<el-select v-model="worldview" class="select" size="default" @change="changeWorldView">
					<el-option key="China" label="China" value="CN"/>
					<el-option key="Japan" label="Japan" value="JP"/>
					<el-option key="India" label="India" value="IN"/>
					<el-option key="United States" label="United States" value="US"/>
				</el-select>
			</span>
			<el-divider />
		</el-collapse-item>

		<!-- Detection Settings -->
		<el-collapse-item title="Detection Settings" name="Detection Settings">
			<span class="single-drawer-item">
				Download Source
				<el-select v-model="downloadSource" class="select" size="default" @change="changeDownloadSource">
					<el-option key="Bing Map" value="Bing Map"/>
					<el-option key="Google Map" value="Google Map"/>
					<el-option key="ESRI" value="ESRI"/>
				</el-select>
			</span>
			<el-divider />
			
			<span class="single-drawer-item">
				Max Grids
				<el-input-number v-model="maxGrids" :min="1" :step="1000" @change="changeMaxGrids" class="select"/>
			</span>
			<el-divider />

			<span class="single-drawer-item">
				Zoom Level
				<el-input-number v-model="zoom" :min="0" :max="24" @change="changeZoom" class="select"/>
			</span>
			<el-divider />

            <span class="single-drawer-item">
				GPU Number
				<el-input-number v-model="gpuNumber" :min="0" :max="7" @change="changeGPUNumber" class="select"/>
			</span>
			<el-divider />

			<span class="single-drawer-item">
				Detection Model
				<el-select v-model="detectionModel" class="select" size="default" @change="changeDetectionModel">
					<el-option key="HRNet" value="HRNet"/>
					<el-option key="DLinkNet" value="DLinkNet"/>
					<el-option key="KDVec" value="KDVec"/>
				</el-select>
			</span>
			<el-divider />
		</el-collapse-item>
	</el-collapse>

	<div class="actions">
		<el-button type="primary" text @click="resetDefaults">Reset to Defaults</el-button>
		<el-button @click="reverseSettingDrawer">Cancel</el-button>
	</div>
	
</el-drawer>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from 'vuex';
import { previewGrid, removeLayer, removeSource } from '~/composables/previewGrid'
import { ElMessage } from 'element-plus'

const store = useStore()

const showSettingDrawer = ref(false)

// open setting drawer
const reverseSettingDrawer = () => showSettingDrawer.value = !showSettingDrawer.value

// change language
const language = ref('English')
const changeLanguage = (value) => {
	store.state.map.setLayoutProperty('country-label', 'text-field', ['get', `name_${value}`])
}

// change map projection
const projection = ref('globe')
const changeMapProjection = (value) => {
	store.state.map.setProjection(value)
}

// change map style
const style = ref('satellite streets')
const changeMapStyle = (value) => {
	if (value === 'satellite') {
		store.state.map.setStyle('mapbox://styles/mapbox/satellite-v9')
	}
	else if (value === 'satellite street') {
		store.state.map.setStyle('mapbox://styles/mapbox/satellite-streets-v12')
	}
	else if (value === 'streets') {
		store.state.map.setStyle('mapbox://styles/mapbox/streets-v12')
	}
	else if (value === 'light') {
		store.state.map.setStyle('mapbox://styles/mapbox/light-v11')
	}
	else if (value === 'dark') {
		store.state.map.setStyle('mapbox://styles/mapbox/dark-v11')
	}
}

// change world view
const worldview = ref('None')
const changeWorldView = (value) => filterLayers(value)
function filterLayers(worldview) {
	// The "admin-0-boundary-disputed" layer shows boundaries
	// at this level that are known to be disputed.
	store.state.map.setFilter('admin-0-boundary-disputed', [
		'all',
		['==', ['get', 'disputed'], 'true'],
		['==', ['get', 'admin_level'], 0],
		['==', ['get', 'maritime'], 'false'],
		['match', ['get', 'worldview'], ['all', worldview], true, false]
	]);
	// The "admin-0-boundary" layer shows all boundaries at
	// this level that are not disputed.
	store.state.map.setFilter('admin-0-boundary', [
		'all',
		['==', ['get', 'admin_level'], 0],
		['==', ['get', 'disputed'], 'false'],
		['==', ['get', 'maritime'], 'false'],
		['match', ['get', 'worldview'], ['all', worldview], true, false]
	]);
	// The "admin-0-boundary-bg" layer helps features in both
	// "admin-0-boundary" and "admin-0-boundary-disputed" stand
	// out visually.
	store.state.map.setFilter('admin-0-boundary-bg', [
		'all',
		['==', ['get', 'admin_level'], 0],
		['==', ['get', 'maritime'], 'false'],
		['match', ['get', 'worldview'], ['all', worldview], true, false]
	]);
}

// change download source
const downloadSource = ref('Bing Map')
const changeDownloadSource = (value) => {
	store.commit('SET_DownloadSource', value)
}

// change max grids
const maxGrids = ref(50000)
const changeMaxGrids = (value) => {
	store.commit('SET_MaxGrids', value)
}

// change zoom level
const zoom = ref(17)
const changeZoom = (value) => {
	store.commit('SET_Zoom', value)
	let total = previewGrid(store.state.maxGrids)
	if (total === null) {
		ElMessage({ message: 'The number of grids exceed the maximum value, please reduce the zoom level or increase the max grids', type: 'warning' })
	}
	else if (total !== -1) {
		ElMessage('Total ' + total.toLocaleString() + ' tiles in the region')
	}
}

// change gpu
const gpuNumber = ref(4)
const changeGPUNumber = (value) => {
	store.commit('SET_GPU', value)
}

// change detection model
const detectionModel = ref('KDVec')
const changeDetectionModel = (value) => {
	store.commit('SET_DetectionModel', value)
}

// reset settings to defaults
const resetDefaults = () => {
	language.value = 'English'
	store.state.map.setLayoutProperty('country-label', 'text-field', ['get', `name_en`])
	projection.value = 'globe'
	store.state.map.setProjection('globe')
	style.value = 'satellite streets'
	store.state.map.setStyle('mapbox://styles/mapbox/satellite-streets-v12')
	downloadSource.value = 'Bing Map'
	store.commit('SET_DownloadSource', 'Bing Map')
	maxGrids.value = 50000
	store.commit('SET_MaxGrids', 50000)
	zoom.value = 17
	store.commit('SET_Zoom', 17)
    gpuNumber.value = 4
    store.commit('SET_GPU', 4)
	removeLayer("grid-preview")
    removeSource("grid-preview")
	detectionModel.value = 'KDVec'
	store.commit('SET_DetectionModel', 'KDVec')
}

defineExpose({
	reverseSettingDrawer
})

</script>

<style scoped>
.drawer-title {
	font-weight: bold;
	margin-top: 10px;
	margin-bottom: -35px;
	@apply select-none flex items-center justify-center text-2xl text-gray-600;
}

.settingBody {
	height: 87%;
	overflow-y: auto;
	border-top: 0;
	border-bottom: 0;
	@apply select-none;
}

.single-drawer-item {
	@apply flex items-center px-8;
}

.single-drawer-item .select {
	width: 35%;
	@apply ml-auto mr-2;
}

.single-drawer-item .type_checkbox {
	@apply ml-auto mr-2;
}

.single-drawer-item :deep(.el-input__wrapper) {
	@apply flex ml-auto;
}

.settingBody::-webkit-scrollbar {
	display: none;
}

.actions {
	position: relative;
	display: flex;
	justify-content: center;
	top: 3%;
}

:deep(.el-divider--horizontal) {
	left: 5%;
	width: 88%;
	@apply my-6 relative flex justify-center;
}

:deep(.el-input__wrapper) {
	width: 120px;
}

:deep(.el-collapse) {
	@apply border-0;
}

:deep(.el-collapse-item__header) {
	height: 60px;
	@apply border-0 text-lg text-gray-500 p-5 mb-3 rounded;
}

:deep(.el-collapse-item__header:hover) {
	@apply bg-gray-100;
}

:deep(.el-collapse-item__content) {
	padding-bottom: 0px;
	@apply border-0 flex flex-col justify-center text-base;
}

:deep(.el-collapse-item__wrap) {
	@apply border-0;
}

:deep(.el-checkbox-button__inner) {
	@apply px-2;
}

</style>