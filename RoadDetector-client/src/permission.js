import { router } from '~/router'
import { toast, showFullLoading, hideFullLoading } from '~/composables/util';
import store from './store';


// 全局前置守卫
router.beforeEach(async (to, from, next) => {
	// 显示loading
	showFullLoading()

	// 设置页面标题
	let title = to.meta.title ? to.meta.title : ""
	document.title = title	
	next()
})

// 全局后置钩子
router.afterEach((to, from) => {
	// 隐藏loading
	hideFullLoading()
})
