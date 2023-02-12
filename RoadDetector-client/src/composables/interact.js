import store from '~/store'
import { POST_DownloadTiles, POST_SpliceTiles, POST_DeployModel, POST_RoadDetect } from '~/api/manager';
import { getCurrentTime, getSourceURL } from '~/composables/util';
import { getGrid, previewRect, removeLayer } from '~/composables/previewGrid';
import { ElMessage } from 'element-plus'
import { remove } from 'nprogress';


export function saveBasicInfo() {
	// add basic info to vuex
	let southWest = store.state.draw.getAll().features[0].geometry.coordinates[0][3]
	let northEast = store.state.draw.getAll().features[0].geometry.coordinates[0][1]

	let time = getCurrentTime()
	store.commit('ADD_Layer', {
		time: time.timeString,
		view: true,
		others: {
			layerId: time.timeStamp,
			pointLayerId: 'Point-' + time.timeStamp,
			lineLayerId: 'Line-' + time.timeStamp,
			model: store.state.detectionModel,
			zoom: store.state.zoom,
			mapSource: store.state.downloadSource,
			southWesternLngLat: southWest,
			northEasternLngLat: northEast,
			timeSpent: 0,  // seconds
		}
	})

}


export function DownloadImage() {
	let tiles = getGrid(store.state.zoom, store.state.maxGrids)
	if (tiles === null) {
		ElMessage({ 
			message: 'The number of grids exceed the maximum value, please reduce the zoom level or increase the max grids',
		 	type: 'error',
			showClose: true
		})
		return
	}

	store.commit('SET_DetectionInfo', {
		step: 1,
		sum: tiles.length,
		downloadCount: 0,
		detectionCount: 0,
	})

	removeLayer("grid-preview")

	// deploy model when downloading tiles to save time
	let promises = [deployModel()]

	let promises2 = tiles.map(tile => {
		return new Promise((resolve) => {
			var rect_id = previewRect(tile)
			POST_DownloadTiles({
				download_url: getSourceURL(store.state.downloadSource),
				save_dir: `./save_dir/${store.state.resultInfo.slice(-1)[0].others.layerId}`,
				save_tile_name: `${tile.x}-${tile.y}-.png`,
				x: tile.x,
				y: tile.y,
				z: tile.z,
				time_out: 5
			}).then(response => {
				if (response.status === 200) {
					// store.dispatch('addDownloadCount')
					store.commit('ADD_DownloadCount')
					removeLayer(rect_id)
					resolve()
				}
			})
		})
	})

	return Promise.all(promises.concat(promises2))
}

// splice image tiles
export function spliceImageTiles() {
	return POST_SpliceTiles({
		save_tile_dir: `./save_dir/${store.state.resultInfo.slice(-1)[0].others.layerId}`,
		save_name: "Origin.png",
	})
}

// deploy detection model to GPU at server
export function deployModel() {
	return POST_DeployModel({
		model_name: store.state.detectionModel,
		save_types: store.state.saveTypes,
		image_path: `./save_dir/${store.state.resultInfo.slice(-1)[0].others.layerId}`,
		gpu: 0
	})
}

// road detection
export function RoadDetection() {
	store.commit('MODIFY_Step', 2)
	return POST_RoadDetect()
}


export function drawOnMap() {
	store.commit('MODIFY_Step', 3)
	store.commit('MODIFY_Step', 4)
}