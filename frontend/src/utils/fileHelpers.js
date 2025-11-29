/**
 * Format file size from bytes to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size (e.g., "1.5 MB")
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Validate file type
 * @param {File} file - File to validate
 * @param {string[]} allowedTypes - Array of allowed MIME types or extensions
 * @returns {boolean} True if file type is allowed
 */
export function isValidFileType(file, allowedTypes) {
  if (!file || !allowedTypes) return false

  const fileName = file.name.toLowerCase()
  const fileType = file.type.toLowerCase()

  return allowedTypes.some(type => {
    // Check MIME type
    if (fileType.includes(type.toLowerCase())) return true

    // Check extension
    if (type.startsWith('.') && fileName.endsWith(type.toLowerCase())) return true

    return false
  })
}

/**
 * Validate file size
 * @param {File} file - File to validate
 * @param {number} maxSizeInMB - Maximum file size in MB
 * @returns {boolean} True if file size is within limit
 */
export function isValidFileSize(file, maxSizeInMB) {
  if (!file) return false
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024
  return file.size <= maxSizeInBytes
}

/**
 * Get file extension from filename
 * @param {string} filename - Filename to parse
 * @returns {string} File extension (e.g., "pdf")
 */
export function getFileExtension(filename) {
  if (!filename) return ''
  const parts = filename.split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

/**
 * Create a file object for upload
 * @param {File} file - Original file
 * @param {string} category - File category (optional)
 * @returns {Object} File object with metadata
 */
export function createFileObject(file, category = '') {
  return {
    name: file.name,
    size: file.size,
    type: file.type,
    category: category,
    file: file,
    uploadedAt: new Date().toISOString()
  }
}
