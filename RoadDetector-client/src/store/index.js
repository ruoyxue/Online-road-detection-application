import { createStore } from 'vuex'


const store = createStore({
	state() {
		return {
			map: null,  // map of mapbox
			draw: null,  // draw of mapbox
			maxGrids: 50000,  // max number of grids
			zoom: 17,  // zoom level
			downloadSource: 'Bing Map',  // source for downloading tiles
			detectionModel: 'KDVec',  // road detection model
			saveTypes: ['GeoJson'],  // / result save types
			savePath: '',  // where to save detection results
			detectionInfo: {
				step: -1,
				sum: 0,
				downloadCount: 0,
				detectionCount: 0,
			},
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
		SET_DownloadSource(state, downloadSource) {
			state.downloadSource = downloadSource
		},
		SET_DetectionModel(state, detectionModel) {
			state.detectionModel = detectionModel
		},
		SET_SaveTypes(state, saveTypes) {
			state.saveTypes = saveTypes
		},
		SET_SavePath(state, savePath) {
			state.savePath = savePath
		},
		SET_DetectionInfo(state, detectionInfo) {
			state.detectionInfo = detectionInfo
		},
		ADD_DownloadCount(state) {
			state.detectionInfo.downloadCount++
		},
		ADD_DetectionCount(state) {
			state.detectionInfo.detectionCount++
		},
		MODIFY_Step(state, step) {
			state.detectionInfo.step = step
		},
		SET_LayerView(state, info) {
			state.resultInfo[info.index].view = info.value
		},
		DELETE_Layer(state, index) {
			state.resultInfo.pop(index)
		},
		ADD_Layer(state, layerInfo) {
			state.resultInfo.push(layerInfo)
		},
		SET_Layer_RefLngLat(state, info) {
			state.resultInfo.slice(info.index)[0].others.refLngLat1 = info.refLngLat1
			state.resultInfo.slice(info.index)[0].others.refLngLat2 = info.refLngLat2
		}

	}, actions: {
		addDownloadCount({ commit }) {
			return new Promise((resolve, reject) => {
				store.commit('ADD_DownloadCount')
			})
		},
	}
  })

  export default store
  