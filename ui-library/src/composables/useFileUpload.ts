/**
 * Composable for handling file uploads with validation
 *
 * @example
 * ```typescript
 * const { file, handleUpload, removeFile, error } = useFileUpload({
 *   maxSize: 10 * 1024 * 1024, // 10MB
 *   allowedTypes: ['application/pdf', 'image/jpeg', 'image/png'],
 *   onFileSelect: (file) => formData.value.certificate_of_title = file
 * })
 * ```
 */

import { ref, computed, type Ref } from 'vue'

export interface FileUploadOptions {
  /**
   * Maximum file size in bytes
   * @example 10 * 1024 * 1024 // 10MB
   */
  maxSize: number

  /**
   * Array of allowed MIME types
   * @example ['application/pdf', 'image/jpeg', 'image/png']
   */
  allowedTypes: string[]

  /**
   * Callback when file is successfully selected and validated
   */
  onFileSelect?: (file: File) => void

  /**
   * Callback when file is removed
   */
  onFileRemove?: () => void

  /**
   * Custom error messages
   */
  errorMessages?: {
    fileSize?: string
    fileType?: string
  }
}

export interface FileUploadReturn {
  /** Currently selected file */
  file: Ref<File | null>

  /** File upload handler for input change event */
  handleUpload: (event: Event) => void

  /** Remove currently selected file */
  removeFile: () => void

  /** Current error message if validation failed */
  error: Ref<string | null>

  /** Whether a file is currently selected */
  hasFile: Ref<boolean>

  /** Formatted file size string */
  fileSize: Ref<string>

  /** File name */
  fileName: Ref<string>
}

export function useFileUpload(options: FileUploadOptions): FileUploadReturn {
  const file = ref<File | null>(null)
  const error = ref<string | null>(null)

  const hasFile = computed(() => file.value !== null)

  const fileName = computed(() => file.value?.name || '')

  const fileSize = computed(() => {
    if (!file.value) return ''
    const bytes = file.value.size
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  })

  const handleUpload = (event: Event) => {
    error.value = null
    const input = event.target as HTMLInputElement
    const selectedFile = input.files?.[0]

    if (!selectedFile) {
      file.value = null
      return
    }

    // Validate file size
    if (selectedFile.size > options.maxSize) {
      const maxSizeMB = Math.round(options.maxSize / (1024 * 1024))
      error.value = options.errorMessages?.fileSize ||
        `File size must be less than ${maxSizeMB}MB`
      input.value = '' // Reset input
      return
    }

    // Validate file type
    if (!options.allowedTypes.includes(selectedFile.type)) {
      const allowedExtensions = options.allowedTypes
        .map(type => {
          // Convert MIME type to extension
          const ext = type.split('/')[1]
          return ext.toUpperCase()
        })
        .join(', ')

      error.value = options.errorMessages?.fileType ||
        `Only ${allowedExtensions} files are allowed`
      input.value = '' // Reset input
      return
    }

    // File is valid
    file.value = selectedFile
    options.onFileSelect?.(selectedFile)
    input.value = '' // Reset input to allow re-selecting same file
  }

  const removeFile = () => {
    file.value = null
    error.value = null
    options.onFileRemove?.()
  }

  return {
    file,
    handleUpload,
    removeFile,
    error,
    hasFile,
    fileSize,
    fileName
  }
}

/**
 * Preset configurations for common file upload types
 */
export const FILE_UPLOAD_PRESETS = {
  /** PDF only, max 10MB */
  PDF_10MB: {
    maxSize: 10 * 1024 * 1024,
    allowedTypes: ['application/pdf']
  },

  /** PDF and Word documents, max 20MB */
  DOCUMENTS_20MB: {
    maxSize: 20 * 1024 * 1024,
    allowedTypes: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
  },

  /** PDF and images, max 10MB */
  PDF_IMAGES_10MB: {
    maxSize: 10 * 1024 * 1024,
    allowedTypes: [
      'application/pdf',
      'image/jpeg',
      'image/jpg',
      'image/png'
    ]
  },

  /** Images only, max 5MB */
  IMAGES_5MB: {
    maxSize: 5 * 1024 * 1024,
    allowedTypes: [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif'
    ]
  }
} as const
