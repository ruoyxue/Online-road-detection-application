import { createRouter, createWebHashHistory} from 'vue-router'
import NotFound from '~/pages/404.vue'
import Home from '~/pages/homepage.vue'


// 默认路由，所有用户共享
const routes = [
	{
		path: '/',
		name: 'home page',
		component: Home,
		meta: {
			title: 'Road Detector'
		}
	}, {
		path: '/:pathMatch(.*)*',
		component: NotFound,
		meta: {
			title: '404 Not Found'
		}
	}
]

export const router = createRouter({
    history: createWebHashHistory(),
    routes
})

