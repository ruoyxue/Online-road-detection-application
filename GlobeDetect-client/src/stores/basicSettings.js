import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useBasicSettingsStore = defineStore('basicSettings', () => {
	let maxGrids =  ref(50000)  // max number of grids
	let zoom =  ref(17)  // zoom level
	let gpu = ref(4)  // selected gpu on server
	let downloadSource = ref('Bing Map')  // source for downloading tiles
	let detectionModel = ref('KDVec')  // road detection model
	let terminateFlag = ref(true)  // used to terminate the process of download and detection
	let needDeployModel = ref(true)	 // whether to update detection model on server

	function changeMaxGrids(num) {
		maxGrids.value = num
	}

	function changeZoom(num) {
		zoom.value = num
	}

	function changeGPU(gpuNum) {
		needDeployModel.value = true
		gpu.value = gpuNum
	}

	function changeDownloadSource() {

	}

	function changeTerminateFlag(flag) {
		terminateFlag.value = flag
	}

	function changeDetectionModel(model) {
		needDeployModel.value = true
		detectionModel.value = model
	}

  return { 
		maxGrids, zoom, gpu, needDeployModel, downloadSource, detectionModel, terminateFlag,
		changeGPU, changeDetectionModel
	}
})
