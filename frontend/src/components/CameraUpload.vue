<template>
  <div class="space-y-4">
    <!-- Upload Label -->
    <label class="block">
      <span class="text-sm font-medium text-gray-900">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </span>
      <p v-if="helpText" class="text-xs text-gray-500 mt-1">{{ helpText }}</p>
    </label>

    <!-- Upload Options -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Camera Capture Button -->
      <button
        v-if="allowCamera"
        @click="openCamera"
        type="button"
        class="relative flex items-center justify-center px-6 py-4 border-2 border-dashed border-blue-300 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all group"
        :class="{ 'opacity-50 cursor-not-allowed': uploading }"
        :disabled="uploading"
      >
        <div class="text-center">
          <svg class="mx-auto h-10 w-10 text-blue-500 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <p class="mt-2 text-sm font-medium text-blue-600 group-hover:text-blue-700">Take Photo</p>
          <p class="text-xs text-gray-500">Use camera</p>
        </div>
      </button>

      <!-- File Upload Button -->
      <button
        @click="triggerFileInput"
        type="button"
        class="relative flex items-center justify-center px-6 py-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all group"
        :class="{ 'opacity-50 cursor-not-allowed': uploading }"
        :disabled="uploading"
      >
        <div class="text-center">
          <svg class="mx-auto h-10 w-10 text-gray-400 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="mt-2 text-sm font-medium text-gray-700 group-hover:text-blue-700">Upload File</p>
          <p class="text-xs text-gray-500">Browse {{ multiple ? 'files' : 'file' }}</p>
        </div>
        <input
          ref="fileInput"
          type="file"
          :accept="accept"
          :multiple="multiple"
          @change="handleFileSelect"
          class="hidden"
        />
      </button>
    </div>

    <!-- Upload Progress -->
    <div v-if="uploading" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center space-x-3">
        <svg class="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <div class="flex-1">
          <p class="text-sm font-medium text-blue-900">Uploading...</p>
          <div class="mt-1 w-full bg-blue-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all" :style="{ width: uploadProgress + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Uploaded Files List -->
    <div v-if="files.length > 0" class="space-y-2">
      <TransitionGroup name="list">
        <div
          v-for="(file, index) in files"
          :key="file.name + index"
          class="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg group hover:bg-green-100 transition-colors"
        >
          <div class="flex items-center space-x-3 flex-1 min-w-0">
            <!-- File Icon/Preview -->
            <div class="flex-shrink-0">
              <div v-if="file.preview" class="w-12 h-12 rounded-lg overflow-hidden border-2 border-green-300">
                <img :src="file.preview" :alt="file.name" class="w-full h-full object-cover" />
              </div>
              <div v-else class="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>

            <!-- File Info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ file.name }}</p>
              <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
            </div>

            <!-- Remove Button -->
            <button
              @click="removeFile(index)"
              type="button"
              class="flex-shrink-0 p-2 text-red-600 hover:text-red-800 hover:bg-red-100 rounded-lg transition-colors"
              title="Remove"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Camera Modal -->
    <Teleport to="body">
      <div
        v-if="showCamera"
        class="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
        @click.self="closeCamera"
      >
        <div class="bg-white rounded-2xl max-w-2xl w-full overflow-hidden shadow-2xl">
          <!-- Camera Header -->
          <div class="bg-gray-900 px-6 py-4 flex items-center justify-between">
            <h3 class="text-white font-semibold text-lg">Take Photo</h3>
            <button
              @click="closeCamera"
              class="text-gray-400 hover:text-white transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Camera View -->
          <div class="relative bg-black aspect-video">
            <video
              v-if="!capturedImage"
              ref="videoElement"
              autoplay
              playsinline
              class="w-full h-full object-contain"
            ></video>
            <img
              v-else
              :src="capturedImage"
              alt="Captured"
              class="w-full h-full object-contain"
            />

            <!-- Camera Overlay Grid -->
            <div v-if="!capturedImage" class="absolute inset-0 pointer-events-none">
              <div class="w-full h-full grid grid-cols-3 grid-rows-3">
                <div v-for="i in 9" :key="i" class="border border-white/20"></div>
              </div>
            </div>
          </div>

          <!-- Camera Controls -->
          <div class="bg-gray-900 px-6 py-6">
            <div v-if="!capturedImage" class="flex items-center justify-center space-x-6">
              <button
                @click="capturePhoto"
                type="button"
                class="w-16 h-16 rounded-full bg-white border-4 border-gray-700 hover:border-blue-500 transition-all flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <div class="w-12 h-12 rounded-full bg-blue-500"></div>
              </button>
            </div>
            <div v-else class="flex items-center justify-center space-x-4">
              <button
                @click="retakePhoto"
                type="button"
                class="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
              >
                Retake
              </button>
              <button
                @click="usePhoto"
                type="button"
                class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Use Photo
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"

const props = defineProps({
	label: {
		type: String,
		required: true,
	},
	helpText: {
		type: String,
		default: "",
	},
	modelValue: {
		type: Array,
		default: () => [],
	},
	accept: {
		type: String,
		default: "image/*,.pdf",
	},
	multiple: {
		type: Boolean,
		default: false,
	},
	required: {
		type: Boolean,
		default: false,
	},
	allowCamera: {
		type: Boolean,
		default: true,
	},
	maxSize: {
		type: Number,
		default: 20 * 1024 * 1024, // 20MB
	},
})

const emit = defineEmits(["update:modelValue", "upload"])

const fileInput = ref(null)
const videoElement = ref(null)
const showCamera = ref(false)
const capturedImage = ref(null)
const mediaStream = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)

const files = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

// Trigger file input
const triggerFileInput = () => {
	fileInput.value?.click()
}

// Handle file selection
const handleFileSelect = async (event) => {
	const selectedFiles = Array.from(event.target.files)
	await processFiles(selectedFiles)
	event.target.value = "" // Reset input
}

// Process files
const processFiles = async (selectedFiles) => {
	const validFiles = []

	for (const file of selectedFiles) {
		// Validate file size
		if (file.size > props.maxSize) {
			alert(
				`File ${file.name} exceeds maximum size of ${formatFileSize(props.maxSize)}`,
			)
			continue
		}

		// Create preview for images
		let preview = null
		if (file.type.startsWith("image/")) {
			preview = await createImagePreview(file)
		}

		validFiles.push({
			file: file,
			name: file.name,
			size: file.size,
			type: file.type,
			preview: preview,
			uploadDate: new Date().toISOString(),
		})
	}

	if (validFiles.length > 0) {
		const newFiles = props.multiple
			? [...files.value, ...validFiles]
			: validFiles
		emit("update:modelValue", newFiles)

		// Auto-upload files
		await uploadFiles(validFiles)
	}
}

// Create image preview
const createImagePreview = (file) => {
	return new Promise((resolve) => {
		const reader = new FileReader()
		reader.onload = (e) => resolve(e.target.result)
		reader.onerror = () => resolve(null)
		reader.readAsDataURL(file)
	})
}

// Upload files
const uploadFiles = async (filesToUpload) => {
	uploading.value = true
	uploadProgress.value = 0

	try {
		for (let i = 0; i < filesToUpload.length; i++) {
			const fileData = filesToUpload[i]

			// Simulate upload progress
			const progressInterval = setInterval(() => {
				uploadProgress.value = Math.min(uploadProgress.value + 10, 90)
			}, 100)

			// Emit upload event (parent component should handle actual upload)
			await new Promise((resolve) => {
				emit("upload", fileData, resolve)
			})

			clearInterval(progressInterval)
			uploadProgress.value = ((i + 1) / filesToUpload.length) * 100
		}
	} catch (error) {
		console.error("Upload error:", error)
		alert("Failed to upload files. Please try again.")
	} finally {
		uploading.value = false
		uploadProgress.value = 0
	}
}

// Remove file
const removeFile = (index) => {
	const newFiles = [...files.value]
	newFiles.splice(index, 1)
	emit("update:modelValue", newFiles)
}

// Open camera
const openCamera = async () => {
	try {
		showCamera.value = true
		await startCamera()
	} catch (error) {
		console.error("Camera error:", error)
		alert(
			"Unable to access camera. Please check permissions or upload a file instead.",
		)
		showCamera.value = false
	}
}

// Start camera
const startCamera = async () => {
	try {
		const stream = await navigator.mediaDevices.getUserMedia({
			video: {
				facingMode: "environment",
				width: { ideal: 1920 },
				height: { ideal: 1080 },
			},
			audio: false,
		})

		mediaStream.value = stream

		if (videoElement.value) {
			videoElement.value.srcObject = stream
		}
	} catch (error) {
		throw error
	}
}

// Capture photo
const capturePhoto = () => {
	const video = videoElement.value
	const canvas = document.createElement("canvas")
	canvas.width = video.videoWidth
	canvas.height = video.videoHeight

	const context = canvas.getContext("2d")
	context.drawImage(video, 0, 0, canvas.width, canvas.height)

	capturedImage.value = canvas.toDataURL("image/jpeg", 0.9)
}

// Retake photo
const retakePhoto = () => {
	capturedImage.value = null
}

// Use photo
const usePhoto = async () => {
	if (!capturedImage.value) return

	// Convert base64 to File
	const blob = await (await fetch(capturedImage.value)).blob()
	const file = new File([blob], `photo-${Date.now()}.jpg`, {
		type: "image/jpeg",
	})

	await processFiles([file])
	closeCamera()
}

// Close camera
const closeCamera = () => {
	if (mediaStream.value) {
		mediaStream.value.getTracks().forEach((track) => track.stop())
		mediaStream.value = null
	}
	capturedImage.value = null
	showCamera.value = false
}

// Format file size
const formatFileSize = (bytes) => {
	if (bytes === 0) return "0 Bytes"
	const k = 1024
	const sizes = ["Bytes", "KB", "MB", "GB"]
	const i = Math.floor(Math.log(bytes) / Math.log(k))
	return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
}
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
