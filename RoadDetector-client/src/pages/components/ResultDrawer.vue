<template>
<el-drawer v-model="showResultDrawer" size="25%" :show-close="false">
	<template #header>
		<span class="header">Road Results</span>
	</template>

	<div class="resultDrawerBody">
		<el-empty description="Empty" v-show="showEmpty" class="emptyStatus"/>
		<el-table ref="resultTableRef" :data="$store.state.resultInfo" v-show="!showEmpty" table-layout="auto">
			<el-table-column type="expand" prop="others">
				<template #default="props">
					<el-descriptions direction="vertical" :column="3" border class="flex justify-center">
						<el-descriptions-item label="Start Time" align="center" span="3">
							{{ props.row.time }}
						</el-descriptions-item>
						<el-descriptions-item label="Model" align="center">
							{{ props.row.others.model }}
						</el-descriptions-item>
						<el-descriptions-item label="Zoom Level" align="center">
							{{ props.row.others.zoom }}
						</el-descriptions-item>
						<el-descriptions-item label="Time Spent" align="center">
							{{ (props.row.others.timeSpent / 60).toFixed(2) + ' min' }}
						</el-descriptions-item>
						<el-descriptions-item label="Map Source" align="center">
							{{ props.row.others.mapSource }}
						</el-descriptions-item>
						<el-descriptions-item label="South West" align="center">
							({{ props.row.others.southWesternLngLat[0].toFixed(2) }},
							{{ props.row.others.southWesternLngLat[1].toFixed(2) }})
						</el-descriptions-item>
						<el-descriptions-item label="North East" align="center">
							({{ props.row.others.northEasternLngLat[0].toFixed(2) }},
							{{ props.row.others.northEasternLngLat[1].toFixed(2) }})
						</el-descriptions-item>
						</el-descriptions>
				</template>
			</el-table-column>
			
			<!-- <el-table-column label="Time" prop="time" /> -->
			<el-table-column label="Save Directory Name" prop="others.saveDirName" />
			<el-table-column label="View">
				<template #default="props">
					<el-switch v-model="props.row.view" size="small" @change="changeLayerView(props.$index)"/>
				</template>
			</el-table-column>

			<el-table-column label="Operations">
				<template #default="props">
                    <el-popover placement="bottom" :width="200" :visible="props.row.others.showRenameInput"
                            title="Rename save directory">
                        <template #reference>
                            <el-button type="primary" icon="EditPen" @click="changeRenameInput(props.$index)" circle/>
                        </template>
                        <el-input v-model="newLayerName" placeholder="Please input new name" 
                                @keyup.enter="renameLayer(props.$index)"/>
                    </el-popover>
		
                    <el-button type="success" icon="Location" circle @click="locateLayer(props.$index)"/>
                    <el-button type="danger" icon="Delete" circle @click="deleteLayer(props.$index)"/>
				</template>
			</el-table-column>
		</el-table>
	</div>
</el-drawer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElTable } from 'element-plus'
import { removeLayer, removeSource } from '~/composables/previewGrid'

// TODO: need to read current files at the server side and show in the drawer when website is updated

const store = useStore()
const showResultDrawer = ref(false)

// open/fold result drawer
const reverseResultDrawer = () => showResultDrawer.value = !showResultDrawer.value

// show empty icon
const showEmpty = computed(() => store.state.resultInfo.length === 0)

// result table
const resultTableRef = ref(null)

const changeLayerView = (index) => {
    store.commit('SET_LayerView', {
        index: index,
        value: store.state.resultInfo[index].view
    })
}

const newLayerName = ref('')
const changeRenameInput = (index) => {
    store.commit('SET_ChangeRenameInput', {
        index: index,
        value: !store.state.resultInfo[index].others.showRenameInput
    })
}

const renameLayer = (index) => {
    store.commit('SET_ChangeRenameInput', {
        index: index,
        value: false
    })
    store.dispatch('renameLayer', {
        index: index,
        new_name: newLayerName.value
    }).then(() => {
         newLayerName.value = ''
         ElMessage({
            message: 'Successfully rename the save directory',
            type: 'success',
            showClose: true
         })
    })
}

const locateLayer = (index) => {
	let southWest = store.state.resultInfo[index].others.southWesternLngLat
	let northEast = store.state.resultInfo[index].others.northEasternLngLat
	store.state.map.fitBounds([ southWest, northEast ])
}

const deleteLayer = (index) => {
	store.dispatch('deleteLayer', index)
}

defineExpose({
	reverseResultDrawer
})

</script>

<style scoped>
.header{
	font-weight: bold;
	margin-top: 10px;
	margin-bottom: -35px;
	@apply select-none flex items-center justify-center text-2xl text-gray-600;
}

.resultDrawerBody {
	height: 95%;
	overflow-y: auto;
	@apply select-none;
}

.resultDrawerBody::-webkit-scrollbar {
	display: none;
}

.resultDrawerBody .emptyStatus {
	height: 100%;
	display: flex;
	align-items: center;
}

:deep(.el-descriptions__body) {
	width: 90%;
}

:deep(.el-table__header-wrapper .cell) {
	@apply text-lg text-gray-600 text-center;
}

:deep(.el-table__body .cell) {
	@apply text-base text-gray-500 text-center;
}

</style>