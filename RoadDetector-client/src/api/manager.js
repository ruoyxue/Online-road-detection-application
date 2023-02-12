import axios from "~/axios.js";
import Qs from 'qs'

// Send download request
export function POST_DownloadTiles(info) {
	return axios.post(
		'/tile_download/', {
			download_url: info.download_url,
			save_dir: info.save_dir,
			save_tile_name: info.save_tile_name,
			x: info.x,
			y: info.y,
			z: info.z,
			time_out: info.time_out
		}
	)
}

// splice tiles
export function POST_SpliceTiles(info) {
	return axios.post(
		'/tile_splice/', {
			save_tile_dir: info.save_tile_dir,
			save_name: info.save_name,
		}
	)
}

// deploy detection to gpu
export function POST_DeployModel(info) {
	return axios.post(
		'/road/deploy_model', {
			model_name: info.model_name,
			save_types: info.save_types,
			image_path: info.image_path,
			gpu: info.gpu,
		}
	)
}

// road detect
export function POST_RoadDetect() {
	return axios.post(
		'/road/road_detect'
	)
}