<template>
	<div>
		<div class="toolbar">
			<el-tooltip content="Settings" :hide-after="50" effect="light">
				<el-icon class="button" @click="toggleSettingDrawer"><Setting /></el-icon>
			</el-tooltip>
			<el-tooltip content="Results" :hide-after="50" effect="light">
				<el-icon class="button" @click="toggleResultDrawer"><Tickets /></el-icon>
				
			</el-tooltip>
			<el-tooltip content="Select Region" :hide-after="50" effect="light">
				<el-icon class="button" @click="handleSelectRegion"><Crop /></el-icon>
			</el-tooltip>
			<el-tooltip content="Delete Region" :hide-after="50" effect="light">
				<el-icon class="button" @click="handleClearRegion"><Delete /></el-icon>
			</el-tooltip>
			<el-tooltip content="Preview Grids" :hide-after="50" effect="light">
				<el-icon class="button" @click="handlePreviewGrid"><Grid /></el-icon>
			</el-tooltip>
			<el-tooltip :content="isStart ? 'Start':'Stop'" :hide-after="50" effect="light">
				<el-icon class="button">
					<el-icon v-show="isStart" @click="handleStart" ><CaretRight /></el-icon>
					<el-icon v-show="!isStart" @click="handleStop" ><VideoPause /></el-icon>
				</el-icon>
			</el-tooltip>
		</div>
	
		<!-- Edit Results Drawer -->
		<ResultDrawer ref="resultDrawerRef"/>
		
		<!-- Settings Drawer -->
		<SettingDrawer ref="settingDrawerRef"/>
	</div>
</template>

<script setup>
import { ElTooltip } from "element-plus"
import { ref } from 'vue'
import ResultDrawer from './ResultDrawer.vue'
import SettingDrawer from './SettingDrawer.vue'
import { removeLayer, removeSource, previewGrid } from '@/composables/previewGrid'
import { useMapboxStore } from '@/stores/mapbox'
import { useBasicSettingsStore } from '@/stores/basicSettings'
import { useProgressInfoStore } from '@/stores/progressInfo'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { DownloadImage, spliceImageTiles, StartDetection, drawOnMap } from '@/composables/interact'
import { GET_Progress } from '@/api/manager'

const { draw } = storeToRefs(useMapboxStore())
const { maxGrids, terminateFlag } = storeToRefs(useBasicSettingsStore())
const { setStep, setProgress } = useProgressInfoStore()

// edit result btn
const resultDrawerRef = ref(null)
const toggleResultDrawer = () => resultDrawerRef.value.toggleResultDrawer()

// settings btn
const settingDrawerRef = ref(null)
const toggleSettingDrawer = () => settingDrawerRef.value.toggleSettingDrawer()

// select region btn
const handleSelectRegion = () => {
	removeLayer("grid-preview")
  removeSource("grid-preview")
  
	draw.value.deleteAll()
	draw.value.changeMode('draw_rectangle')
	ElMessage({message: 'Click twice to make a rectangle', showClose: true})
  setStep('Download')
	setProgress(0)
}

// clear region btn
const handleClearRegion = () => {
	if (draw.value.getAll().features.length === 0) {
		ElMessage({ message: 'Please select a region first', type: 'warning', showClose: true})
	}
	removeLayer("grid-preview")
  removeSource("grid-preview")

	draw.value.deleteAll()
	setStep('Download')
	setProgress(0)
}

// preview grids btn
const handlePreviewGrid = () => {
	let total = previewGrid(maxGrids.value)
	if (total === null) {
		ElMessage({ 
			message: 'The number of grids exceed the maximum', 
			type: 'error',
			showClose: true
		})
	}
	else if (total === -1) {
		ElMessage({ message: 'Please select a region first', type: 'warning', showClose: true})
	}
	else {
		ElMessage({message: 'Total ' + total.toLocaleString() + ' tiles in the region', showClose: true})
	}
}

// start btn
let isStart = ref(true)
const handleStart = async () => {
  terminateFlag.value = true
	if (draw.value.getAll().features.length === 0) {
		ElMessage({ message: 'Please select a region first', type: 'warning', showClose: true})
		return
	}
	
	isStart.value = !isStart.value
	await DownloadImage()
	await spliceImageTiles()
	await StartDetection()
	await new Promise(resolve => {
		let interval = setInterval(
			async () => {
				let res = await GET_Progress()
				setProgress(res.data * 100) 
				if (res.data === 1) {
					clearInterval(interval)
					resolve()
				}
			}, 250
		)
	})

  // TODO: need to cancel Promise chain on click of stop button

	drawOnMap()
	isStart.value = !isStart.value
}

// stop btn
const handleStop = () => {
	isStart.value = !isStart.value
  terminateFlag.value = false
  setStep('Download')
	setProgress(0)
	removeLayer("grid-preview")
	removeSource("grid-preview")
	draw.value.deleteAll()
}

</script>

<style scoped>
.toolbar {
	transition: opacity .25s ease-in-out;
	border-radius: 3rem;
	@apply flex justify-between items-center h-14 w-72 p-4 
	select-none bg-gray-300 opacity-30 hover:opacity-100;
}
.toolbar .button {
	transition: all .15s ease-in-out;
	@apply text-2xl cursor-pointer hover:text-cyan-500 hover:font-semibold hover:text-3xl;
}

</style>