import { ElNotification, ElMessageBox } from "element-plus"
// import NProgress from 'nprogress'

// 提示信息

export function toast(info) {
	ElNotification(info)
}

// 消息弹出框
export function showModal(content='提示内容', type='warning', title='') {
	return ElMessageBox.confirm(
		content,
		title,
		{
		  confirmButtonText: 'OK',
		  cancelButtonText: 'Cancel',
		  type: type,
		}
	)		
}

// 显示全屏loading
export function showFullLoading() {
	NProgress.start()
}


// 隐藏全屏loading
export function hideFullLoading() {
	NProgress.done()
}


// get current time
export function getCurrentTime() {
	let time = new Date();
	let year = time.getFullYear();
	let month = time.getMonth()+1;
	let day = time.getDate();
	let hour = time.getHours();
	let minute = time.getMinutes();
	let second = time.getSeconds();
	let timeString_all = year+'-'+(month<10?'0'+month:month)+'-'+(day<10?'0'+day:day)+' '+(hour<10?'0'+hour:hour)+':'+(minute<10?'0'+minute:minute)+':'+(second<10?'0'+second:second)
	let timeString = (hour<10?'0'+hour:hour)+': '+(minute<10?'0'+minute:minute)+': '+(second<10?'0'+second:second)
	let timeStamp = new Date(timeString_all).getTime()
	return {
		timeString: timeString,
		timeStamp: timeStamp
	}
}

// get map source url by source name
export const getSourceURL = (value) => {
	if (value === 'Bing Map') {
		return 'http://ecn.t0.tiles.virtualearth.net/tiles/a{quad}.jpeg?g=129&mkt=en&stl=H'
	}
	else if (value === 'Google Map') {
		return 'https://mt0.google.com/vt?lyrs=s&x={x}&s=&y={y}&z={z}'
	}
	else if (value === 'ESRI') {
		return 'http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
	}
	else {
		throw new Error('Invalid source name')
	}
}