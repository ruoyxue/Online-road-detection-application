import { POST_DownloadTiles, POST_SpliceTiles, POST_DeployModel,
         POST_StartDetect, GET_RoadGraph } from '@/api/manager';
import { getCurrentTime, getSourceURL } from '@/composables/util';
import { getGrid, previewRect, removeLayer, removeSource } from '@/composables/previewGrid';
import { ElMessage } from 'element-plus'
import { useBasicSettingsStore } from '@/stores/basicSettings'
import { useResultInfoStore } from '@/stores/resultInfo';
import { useMapboxStore } from '@/stores/mapbox'
import { useProgressInfoStore } from '@/stores/progressInfo'
import { storeToRefs } from 'pinia'


export function DownloadImage() {
	const { 
		maxGrids, zoom, gpu, needDeployModel, downloadSource, detectionModel, terminateFlag
	} = storeToRefs(useBasicSettingsStore())
	const { addResultLayer } = useResultInfoStore()
	const { setStep, setProgress } = useProgressInfoStore()
	let startTime = getCurrentTime()

  let tiles = getGrid(zoom.value, maxGrids.value)
	if (tiles === null) {
		ElMessage({ 
			message: 'The number of grids exceed the maximum value, please reduce the zoom level or increase the max grids',
		 	type: 'error',
			showClose: true
		})
		return
	}

	let northWest = tiles[0].rect.getSouthWest(),
			southEast = tiles.slice(-1)[0].rect.getNorthEast(),
			southWest = [ northWest.lng, southEast.lat ],
			northEast = [ southEast.lng, northWest.lat ]

	addResultLayer ({
		time: startTime.timeString,
		view: true,
		others: {
			saveDirName: startTime.timeStamp,
			pointLayerId: 'Point-' + startTime.timeStamp,
			lineLayerId: 'Line-' + startTime.timeStamp,
			sourceId: 'Source-' + startTime.timeStamp,
			model: detectionModel.value,
			zoom: zoom.value,
			mapSource: downloadSource.value,
			southWesternLngLat: southWest,
			northEasternLngLat: northEast,
			northWesternLngLat: [northWest.lng, northWest.lat],
			southEasternLngLat: [southEast.lng, southEast.lat],
			startTime: startTime.timeStamp,
			timeSpent: 0,  // seconds
			showRenameInput: false  // whether to show rename box in result drawer
		}
	})

  setStep('Download')
	setProgress(0)
    
	let count = 0
	let tileSum = tiles.length

	removeLayer("grid-preview")
  removeSource("grid-preview")
    
	// deploy model when downloading tiles to save time
	let promises = []
	if (needDeployModel.value) {
		needDeployModel.value = false
		promises.push(new Promise((resolve) => {
			deployModel().then(res => resolve())
		}))
	}
    
	let promises2 = tiles.map(tile => {
		return new Promise((resolve, reject) => {
			var rect_id = previewRect(tile)
			POST_DownloadTiles({
				download_url: getSourceURL(downloadSource.value),
				save_dir: `./road/save_dir/${startTime.timeStamp}`,
				save_tile_name: `${tile.x}-${tile.y}-.png`,
				x: tile.x,
				y: tile.y,
				z: tile.z,
				time_out: 5
			}).then((response) => {
				if (response.status === 200) {
					count += 1
					setProgress((count / tileSum) * 100)
					removeLayer(rect_id)
					removeSource(rect_id)
					resolve()
				}
				if (!terminateFlag.value) {
					reject('Process has been stopped')
				}
			})
		})
	})
	return Promise.all(promises.concat(promises2))
}

// splice image tiles
export function spliceImageTiles() {
	const { resultInfo } = storeToRefs(useResultInfoStore())

	return POST_SpliceTiles({
		save_tile_dir: `./road/save_dir/${resultInfo.value.slice(-1)[0].others.saveDirName}`,
		save_name: "Origin.png",
	})
}

// deploy detection model to GPU at server
export function deployModel() {
	const { gpu, detectionModel } = storeToRefs(useBasicSettingsStore())
	return POST_DeployModel({
		model_name: detectionModel.value,
		gpu: gpu.value
	})
}

// road detection
export function StartDetection() {
	const { resultInfo } = storeToRefs(useResultInfoStore())
	const { setStep, setProgress } = useProgressInfoStore()
	setStep('Detection')
	setProgress(0)

	return POST_StartDetect({
		image_path: `./road/save_dir/${resultInfo.value.slice(-1)[0].others.saveDirName}`,
		northwest_lnglat: resultInfo.value.slice(-1)[0].others.northWesternLngLat,
		southeast_lnglat: resultInfo.value.slice(-1)[0].others.southEasternLngLat,
	})
}

// draw road graph on map
export function drawOnMap() {
	const { map } = storeToRefs(useMapboxStore())
	const { resultInfo, setResultLayerTimeSpent } = storeToRefs(useResultInfoStore())

	GET_RoadGraph().then(res => {
			let data = res.data
			if (data.features.length === 0) {
					ElMessage({
							message: 'None road is detected',
							type: 'info',
							showClose: true,
					})
			} else {
					ElMessage({
							message: 'Road is detected successfully',
							type: 'success',
							showClose: true,
					})
			}
			map.value.addSource(
					resultInfo.value.slice(-1)[0].others.sourceId, 
					{ 'type': 'geojson', 'data': data }
			)

			map.value.addLayer({
					'id': resultInfo.value.slice(-1)[0].others.lineLayerId,
					'type': 'line',
					'source': resultInfo.value.slice(-1)[0].others.sourceId,
					'paint': {
							'line-color': "rgb(0,188,255)",
							'line-width': 3
					},
					'filter': ['==', '$type', 'LineString']
			});

			map.value.addLayer({
					'id': resultInfo.value.slice(-1)[0].others.pointLayerId,
					'type': 'circle',
					'source': resultInfo.value.slice(-1)[0].others.sourceId,
					'paint': {
							'circle-radius': 4,
							'circle-color': "rgb(251,238,75)"
					},
					'filter': ['==', '$type', 'Point']
			});

			let timeSpent = getCurrentTime().timeStamp - resultInfo.value.slice(-1)[0].others.startTime
			
			setResultLayerTimeSpent(timeSpent / 1000)
	})
}