import axios from "axios";
import store from '~/store'

const service = axios.create({
  baseURL: '/api'
})

// // 添加请求拦截器
// service.interceptors.request.use(function (config) {
// 	// 向header头中自动添加token
// 	const token = getToken()
// 	if(token){
// 		config.headers['token'] = token
// 	}
//     return config;
//   }, function (error) {
//     return Promise.reject(error);
//   });

// // 添加响应拦截器
// service.interceptors.response.use(function (response) {
//     return response.data.data;
//   }, function (error) {
// 	toast(error.response.data.msg || "Request Failed", 'error')

// 	if (error.response.data.msg == '非法token，请先登录！'){
// 		console.log('here')
// 		store.dispatch('logout')
// 			.finally(() => location.reload())
// 	}

//     return Promise.reject(error);
//   });

export default service