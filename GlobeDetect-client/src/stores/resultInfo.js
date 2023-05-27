import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useMapboxStore } from '@/stores/mapbox'
import { storeToRefs } from 'pinia'
import { DELETE_Layer, PUT_RenameLayer } from '@/api/manager'
import { removeLayer, removeSource } from '@/composables/previewGrid';


export const useResultInfoStore = defineStore('resultInfo', () => {
	let resultInfo = ref([])
	const { map, draw } = storeToRefs(useMapboxStore())
	
	function addResultLayer(layerInfo) {
		resultInfo.value.push(layerInfo)
	}

	async function deleteResultLayer(layerIndex) {
		await	DELETE_Layer(store.state.resultInfo[layerIndex].others.saveDirName)		
		draw.value.deleteAll()
		removeLayer(resultInfo.value[layerIndex].others.lineLayerId)
		removeLayer(resultInfo.value[layerIndex].others.pointLayerId)
		removeSource(resultInfo.value[layerIndex].others.sourceId)
		resultInfo.value = deleteEleByIndex(resultInfo.value, layerIndex)
		ElMessage({
				message: 'Successfullt delete the layer',
				type: 'success',
				showClose: true
		})
	}

	async function renameResultLayer(info) {
		await PUT_RenameLayer({
			old_name: resultInfo.value[info.index].others.saveDirName,
			new_name: info.new_name
		})
		resultInfo.value[info.index].others.saveDirName = info.new_name
	}

	function changeRenameBoxFlag(info) {
		resultInfo.value[info.index].others.showRenameInput = info.value
	}

	// set if the result layer is visible
	// info: { index, value }
	function setLayerView(info) {
		resultInfo.value[info.index].view = info.value
			if(info.value) {
				map.value.setLayoutProperty(
					resultInfo.value[info.index].others.pointLayerId, 
					"visibility", 
					"visible"
				)
				map.value.setLayoutProperty(
					resultInfo.value[info.index].others.lineLayerId, 
					"visibility", 
					"visible"
				)
			} else {
				map.value.setLayoutProperty(
					resultInfo.value[info.index].others.pointLayerId, 
					"visibility", 
					"none"
				)
				map.value.setLayoutProperty(
					resultInfo.value[info.index].others.lineLayerId, 
					"visibility", 
					"none"
				)
			}
	}

	function setResultLayerTimeSpent(timeSpent) {
		resultInfo.value.slice(-1)[0].others.timeSpent = timeSpent
	}

  return { 
		resultInfo, setLayerView, addResultLayer, deleteResultLayer, renameResultLayer,
		changeRenameBoxFlag, setResultLayerTimeSpent
	}
})
