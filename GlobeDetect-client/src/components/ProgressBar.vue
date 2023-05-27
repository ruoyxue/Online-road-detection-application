<template>
	<div>
		<el-progress type="circle" :percentage="progress" :stroke-width="12.5"
			:width="150" :color="progressBarColors" id="progress-bar" :style="{ opacity: opacity }">
			<span id="progress__label">{{ step }}</span>
	 	</el-progress>
	</div>
</template>

<script setup>
import { useProgressInfoStore } from '@/stores/progressInfo'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

const { step, progress } = storeToRefs(useProgressInfoStore())

const opacity = computed(() => {
	return step.value == 'Download' && progress.value == 0 ? '0.3' : '1'
})

const progressBarColors = [
    { color: '#f56c6c', percentage: 20 },
    { color: '#e6a23c', percentage: 40 },
    { color: '#5cb87a', percentage: 60 },
    { color: '#6f7ad3', percentage: 80 },
    { color: '#1989fa', percentage: 100 },
]

</script>

<style scoped>
#progress__label {
	font-size: 1.3rem;
	@apply text-white font-bold transition-opacity;
}

</style>