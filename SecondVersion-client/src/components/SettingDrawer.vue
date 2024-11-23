<template>
<el-drawer v-model="showSettingDrawer" size="500" :show-close="false">
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
				<el-input-number v-model="gpu" :min="0" :max="7" @change="changeGPU" class="select"/>
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
		<el-button @click="toggleSettingDrawer">Cancel</el-button>
	</div>
	
</el-drawer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { previewGrid, removeLayer, removeSource } from '@/composables/previewGrid'
import { ElMessage } from 'element-plus'
import { useMapboxStore } from '@/stores/mapbox'
import { useBasicSettingsStore } from '@/stores/basicSettings'
import { storeToRefs } from 'pinia'

const { map } = storeToRefs(useMapboxStore())

const basicSettingsStore = useBasicSettingsStore()
const { 
	maxGrids, zoom, gpu, downloadSource, detectionModel, permitFlag 
} = storeToRefs(basicSettingsStore)
const { changeGPU, changeDetectionModel } = basicSettingsStore

const showSettingDrawer = ref(false)

// toggle setting drawer
const toggleSettingDrawer = () => showSettingDrawer.value = !showSettingDrawer.value

// change language
const language = ref('English')
const changeLanguage = (value) => {
	map.value.setLayoutProperty('country-label', 'text-field', ['get', `name_${value}`])
}

// change map projection
const projection = ref('globe')
const changeMapProjection = (value) => {
	map.value.setProjection(value)
}

// change map style
const style = ref('satellite streets')
const changeMapStyle = (value) => {
	if (value === 'satellite') {
		map.value.setStyle('mapbox://styles/mapbox/satellite-v9')
	}
	else if (value === 'satellite street') {
		map.value.setStyle('mapbox://styles/mapbox/satellite-streets-v12')
	}
	else if (value === 'streets') {
		map.value.setStyle('mapbox://styles/mapbox/streets-v12')
	}
	else if (value === 'light') {
		map.value.setStyle('mapbox://styles/mapbox/light-v11')
	}
	else if (value === 'dark') {
		map.value.setStyle('mapbox://styles/mapbox/dark-v11')
	}
}

// change world view
const worldview = ref('None')
function changeWorldView(worldview) {
	// The "admin-0-boundary-disputed" layer shows boundaries
	// at this level that are known to be disputed.
	map.value.setFilter('admin-0-boundary-disputed', [
		'all',
		['==', ['get', 'disputed'], 'true'],
		['==', ['get', 'admin_level'], 0],
		['==', ['get', 'maritime'], 'false'],
		['match', ['get', 'worldview'], ['all', worldview], true, false]
	]);
	// The "admin-0-boundary" layer shows all boundaries at
	// this level that are not disputed.
	map.value.setFilter('admin-0-boundary', [
		'all',
		['==', ['get', 'admin_level'], 0],
		['==', ['get', 'disputed'], 'false'],
		['==', ['get', 'maritime'], 'false'],
		['match', ['get', 'worldview'], ['all', worldview], true, false]
	]);
	// The "admin-0-boundary-bg" layer helps features in both
	// "admin-0-boundary" and "admin-0-boundary-disputed" stand
	// out visually.
	map.value.setFilter('admin-0-boundary-bg', [
		'all',
		['==', ['get', 'admin_level'], 0],
		['==', ['get', 'maritime'], 'false'],
		['match', ['get', 'worldview'], ['all', worldview], true, false]
	]);
}

// change download source
const changeDownloadSource = (value) => {
	downloadSource.value = value
}

// change max grids
const changeMaxGrids = (value) => {
	maxGrids.value = value
}

// change zoom level
const changeZoom = (value) => {
	zoom.value = value
	let total = previewGrid(maxGrids.value)
	if (total === null) {
		ElMessage({ message: 'The number of grids exceed the maximum value, please reduce the zoom level or increase the max grids', type: 'warning' })
	}
	else if (total !== -1) {
		ElMessage('Total ' + total.toLocaleString() + ' tiles in the region')
	}
}

// reset settings to defaults
const resetDefaults = () => {
	language.value = 'English'
	map.value.setLayoutProperty('country-label', 'text-field', ['get', `name_en`])
	projection.value = 'globe'
	map.value.setProjection('globe')
	style.value = 'satellite streets'
	map.value.setStyle('mapbox://styles/mapbox/satellite-streets-v12')
	downloadSource.value = 'Bing Map'
	maxGrids.value = 50000
	zoom.value = 17
	worldview.value = 'China'
	changeWorldView('CN')
	changeGPU(4)
	changeDetectionModel('KDVec')
	removeLayer("grid-preview")
  removeSource("grid-preview")
}

defineExpose({
	toggleSettingDrawer
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