import { ref } from 'vue'
import { defineStore } from 'pinia'


export const useProgressInfoStore = defineStore('progressInfo', () => {
	let step = ref('Download')  // Download image or road detection
	let progress = ref(0)  // Progress percentage	

	function setStep(stepInfo) {
		step.value = stepInfo
	}

	function setProgress(progressInfo) {
		progress.value = progressInfo
	}

  return { step, progress, setStep, setProgress }
})
