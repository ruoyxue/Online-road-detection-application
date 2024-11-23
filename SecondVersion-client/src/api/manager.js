import axios from "axios";
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
			gpu: info.gpu,
		}
	)
}

// start detect
export function POST_StartDetect(info) {
	return axios.post(
		'/road/start_detect', {
			image_path: info.image_path,
			northwest_lnglat: info.northwest_lnglat,
			southeast_lnglat: info.southeast_lnglat,
		}
	)
}

// get progress on server
export function GET_Progress() {
	return axios.get('/road/get_progress')
}

// show graph
export function GET_RoadGraph() {
	return axios.get('/road/show_graph')
}

// delete layer
export function DELETE_Layer(save_name) {
	return axios.put(
		'/road/delete_layer', {
			save_dir: save_name
		}
	)
}

// rename save directory name of the layer
export function PUT_RenameLayer(info) {
    return axios.put(
        '/road/rename_layer', {
            old_name: info.old_name,
            new_name: info.new_name,
        }
    )
}
