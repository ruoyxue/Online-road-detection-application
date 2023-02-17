<template>
<div class="f-header">
	<!-- logo -->
	<span class="logo">
		<el-icon class="mr-2"><ChromeFilled /></el-icon>
		<span class="select-none">Road Detector</span>
	</span>

	<!-- Select a Region -->
	<el-tooltip effect="dark" content="Select a Region" placement="bottom">
		<el-icon class="icon-btn" @click.stop="selectRegionBtn"><Scissor /></el-icon>
	</el-tooltip>

	<!-- Clear Region -->
	<el-tooltip effect="dark" content="Clear Region" placement="bottom">
		<el-icon class="icon-btn" @click.stop="clearRegionBtn"><Delete /></el-icon>
	</el-tooltip>

	<!-- Preview Grids -->
	<el-tooltip effect="dark" content="Preview Grids" placement="bottom">
		<el-icon class="icon-btn" @click.stop="previewGridBtn"><Grid /></el-icon>
	</el-tooltip>

	<!-- start -->
	<el-tooltip effect="dark" :content="isStart ? 'Start':'Stop'" placement="bottom">
		<el-icon class="icon-btn">
			<el-icon v-show="isStart" size="20px" @click="startBtn" class="icon-btn"><CaretRight/></el-icon>
			<el-icon v-show="!isStart" @click="stopBtn" class="icon-btn">
				<svg t="1675871811942" class="icon" viewBox="0 0 1024 1024" version="1.1" 
					xmlns="http://www.w3.org/2000/svg" p-id="9234" data-spm-anchor-id="a313x.7781069.0.i0" 
					width="200" height="200"><path d="M256 256h512v512H256z" p-id="9235">
					</path>
				</svg>
			</el-icon>
		</el-icon>
	</el-tooltip>

	<!-- Edit Results -->
	<el-tooltip effect="dark" content="Edit Results" placement="bottom">
		<el-icon class="icon-btn" @click="editResultBtn"><Edit /></el-icon>
	</el-tooltip>

	<!-- Setting -->
	<el-tooltip effect="dark" content="Settings" placement="bottom">
		<el-icon class="icon-btn ml-auto" @click="settingBtn"><Setting /></el-icon>
	</el-tooltip>

	<!-- View -->
	<el-tooltip effect="dark" :content="isView ? 'View':'Hide'" placement="bottom">
		<el-icon class="icon-btn" @click="changeisView">
			<View v-show="isView"/>
			<Hide v-show="!isView"/>
		</el-icon>
	</el-tooltip>

	<!-- Full Screen -->
	<el-tooltip effect="dark" :content="FullScreenBtnName" placement="bottom">
		<el-icon class="icon-btn" @click="toggle">
			<FullScreen />
		</el-icon>	
	</el-tooltip>

	<!-- Edit Results Drawer -->
	<ResultDrawer ref="resultDrawerRef"></ResultDrawer>
	
	<!-- Settings Drawer -->
	<SettingDrawer ref="settingDrawerRef"></SettingDrawer>

</div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useFullscreen } from '@vueuse/core'
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { removeLayer, removeSource, previewGrid } from '~/composables/previewGrid'
import ResultDrawer from '~/pages/components/ResultDrawer.vue'
import SettingDrawer from '~/pages/components/SettingDrawer.vue'
import { DownloadImage, spliceImageTiles, StartDetection, drawOnMap } from '~/composables/interact'
import { GET_Progress } from '~/api/manager'
import { getCurrentTime } from '~/composables/util'

const router = useRouter()
const store = useStore()

// fullscreen
const { isFullscreen, toggle } = useFullscreen()
const FullScreenBtnName = computed(() => isFullscreen.value ? 'Exit' : 'FullScreen')

// edit result btn
const resultDrawerRef = ref(null)
const editResultBtn = () => resultDrawerRef.value.reverseResultDrawer()

// settings btn
const settingDrawerRef = ref(null)
const settingBtn = () => settingDrawerRef.value.reverseSettingDrawer()

// select region btn
const selectRegionBtn = () => {
	removeLayer("grid-preview")
    removeSource("grid-preview")
    
	store.state.draw.deleteAll()
	store.state.draw.changeMode('draw_rectangle')
	ElMessage({message: 'Click twice to make a rectangle', showClose: true})
    store.commit('SET_Step', 'Download')
	store.commit('SET_Progress', 0)
}

// clear region btn
const clearRegionBtn = () => {
	if (store.state.draw.getAll().features.length === 0) {
		ElMessage({ message: 'Please select a region first', type: 'warning', showClose: true})
	}
	removeLayer("grid-preview")
    removeSource("grid-preview")

	store.state.draw.deleteAll()
	store.commit('SET_Step', 'Download')
	store.commit('SET_Progress', 0)
}

// preview grids btn
const previewGridBtn = () => {
	let total = previewGrid(store.state.maxGrids)
	if (total === null) {
		ElMessage({ 
			message: 'The number of grids exceed the maximum value, please reduce the zoom level or increase the max grids', 
			type: 'error',
			showClose: true
		})
	}
	else if (total === -1) {
		ElMessage({ message: 'Please select a region first', type: 'warning', showClose: true})
	}
	else {
		ElMessage({message: 'Total ' + total.toLocaleString() + ' tiles in the region', showClose: true})
	}
}

// start stop btn
let isStart = ref(true)
const startBtn = async () => {
    store.commit('SET_PermitFlag', true)
	if (store.state.draw.getAll().features.length === 0) {
		ElMessage({ message: 'Please select a region first', type: 'warning', showClose: true})
		return
	}
	
	isStart.value = !isStart.value
    await DownloadImage()
    await spliceImageTiles()
    await StartDetection()
    await new Promise(resolve => {
        let interval = setInterval(
            async () => {
                let res = await GET_Progress()
                store.commit('SET_Progress', res.data * 100)
                if (res.data === 1) {
                    clearInterval(interval)
                    resolve()
                }
            }, 250
        )
    })
    
    // TODO: need to cancel Promise chain on click of stop button

    drawOnMap()
    isStart.value = !isStart.value
}


const stopBtn = () => {
    store.commit('SET_PermitFlag', false)
	isStart.value = !isStart.value
    store.commit('SET_Step', 'Download')
	store.commit('SET_Progress', 0)
	removeLayer("grid-preview")
	store.state.draw.deleteAll()
}

// view
const isView = ref(true)
const changeisView = () => {
	isView.value = !isView.value
	store.state.resultInfo.forEach((value, index) => {
		store.commit('SET_LayerView', {
			index: index,
			value: isView.value
		})
	})
}


</script>

<style scoped lang='postcss'>
.f-header{
	@apply flex items-center bg-neutral-800 text-light-50 fixed top-0 left-0 right-0;
	height: 48px;
}

.logo{
	@apply flex justify-center items-center text-xl;
	width: 220px;
}

.icon-btn{
	@apply flex justify-center items-center ;
	width: 48px;
	height: 48px;
	cursor: pointer;
}

.icon-btn:hover{
	@apply bg-neutral-500;
}

:deep(.el-overlay) {
	top: 48px;
}

</style>