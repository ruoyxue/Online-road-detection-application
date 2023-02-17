import { createStore } from 'vuex'
import { removeLayer, removeSource } from '~/composables/previewGrid';
import { DELETE_Layer, PUT_RenameLayer } from '~/api/manager';
import { deleteEleByIndex } from '~/composables/util'
import { ElMessage } from 'element-plus';


const store = createStore({
	state() {
		return {
			map: null,  // map of mapbox
			draw: null,  // draw of mapbox
			maxGrids: 50000,  // max number of grids
			zoom: 17,  // zoom level
            gpu: 4,  // selected gpu on server
            needDeployModel: true,  // whether to update detection model on server
			downloadSource: 'Bing Map',  // source for downloading tiles
			detectionModel: 'KDVec',  // road detection model
			detectionInfo: {
				step: 'Download',
				progress: 0,
			},
            permitFlag: true,  // used for stop button
			resultInfo: [],
			
		}
	}, mutations: {
		SET_Map(state, map) {
			state.map = map
		},
		SET_Draw(state, draw) {
			state.draw = draw
		},
		SET_MaxGrids(state, maxGrids) {
			state.maxGrids = maxGrids
		},
		SET_Zoom(state, zoom) {
			state.zoom = zoom
		},
        SET_GPU(state, gpu) {
            state.gpu = gpu
            state.needDeployModel = true
        },
        SET_NeedDeployModel(state, value) {
            state.needDeployModel = value
        },
        SET_PermitFlag(state, value) {
            state.permitFlag = value
        },
		SET_DownloadSource(state, downloadSource) {
			state.downloadSource = downloadSource
		},
		SET_DetectionModel(state, detectionModel) {
			state.detectionModel = detectionModel
            state.needDeployModel = true
		},
        SET_LastTimeStamp(state, timeSpent) {
            state.resultInfo.slice(-1)[0].others.timeSpent = timeSpent
        },
		SET_Step(state, step) {
			state.detectionInfo.step = step
		},
		SET_Progress(state, progress) {
			state.detectionInfo.progress = progress
		},
		SET_LayerView(state, info) {
			state.resultInfo[info.index].view = info.value
            if (info.value) {
                state.map.setLayoutProperty(
                    state.resultInfo[info.index].others.pointLayerId, 
                    "visibility", 
                    "visible"
                )
                state.map.setLayoutProperty(
                    state.resultInfo[info.index].others.lineLayerId, 
                    "visibility", 
                    "visible"
                )
            } else {
                state.map.setLayoutProperty(
                    state.resultInfo[info.index].others.pointLayerId, 
                    "visibility", 
                    "none"
                )
                state.map.setLayoutProperty(
                    state.resultInfo[info.index].others.lineLayerId, 
                    "visibility", 
                    "none"
                )
            }
		},
		REMOVE_Layer(state, index) {
			state.resultInfo = deleteEleByIndex(state.resultInfo, index)
		},
        RENAME_SaveDir(state, info) {
            state.resultInfo[info.index].others.saveDirName = info.new_name
        },
		ADD_Layer(state, layerInfo) {
			state.resultInfo.push(layerInfo)
		},
        SET_ChangeRenameInput(state, info) {
            state.resultInfo[info.index].others.showRenameInput = info.value
        }
	}, actions: {
        deleteLayer({commit}, index) {
            return new Promise( resolve => {
                DELETE_Layer(store.state.resultInfo[index].others.saveDirName)
                    .then(() => {
                        store.state.draw.deleteAll()
                        removeLayer(store.state.resultInfo[index].others.lineLayerId)
                        removeLayer(store.state.resultInfo[index].others.pointLayerId)
                        removeSource(store.state.resultInfo[index].others.sourceId)
                        store.commit('REMOVE_Layer', index)
                        ElMessage({
                            message: 'Successfullt delete the layer',
                            type: 'success',
                            showClose: true
                        })
                        resolve()
                    })
			})
        },
        renameLayer({commit}, info) {
            return new Promise( resolve => {
                PUT_RenameLayer({
                    old_name: store.state.resultInfo[info.index].others.saveDirName,
                    new_name: info.new_name
                }).then(() => {
                    store.commit('RENAME_SaveDir', info)
                    resolve()
                })
                
            })
        }
	}
})

  export default store
  