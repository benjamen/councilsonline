import { apiClient } from "./base"

/**
 * Document Service
 * Handles file uploads, attachments, and document management
 */
export class DocumentService {
	/**
	 * Upload file to Frappe
	 * @param {File} file - File object
	 * @param {Object} options - Upload options
	 * @param {string} options.doctype - Parent DocType
	 * @param {string} options.docname - Parent document name
	 * @param {string} options.fieldname - Field name for attachment
	 * @param {boolean} options.is_private - Whether file is private (default: true)
	 * @returns {Promise<Object>} Uploaded file document
	 */
	async uploadFile(file, options = {}) {
		return apiClient.uploadFile(file, {
			is_private: true,
			...options,
		})
	}

	/**
	 * Upload multiple files
	 * @param {FileList|Array<File>} files - Files to upload
	 * @param {Object} options - Upload options (same as uploadFile)
	 * @returns {Promise<Array<Object>>} Uploaded file documents
	 */
	async uploadMultipleFiles(files, options = {}) {
		const uploadPromises = Array.from(files).map((file) =>
			this.uploadFile(file, options),
		)
		return Promise.all(uploadPromises)
	}

	/**
	 * Get file by name
	 * @param {string} fileName - File document name
	 * @returns {Object} Frappe resource
	 */
	getFile(fileName) {
		return apiClient.createResource({
			url: "frappe.client.get",
			params: {
				doctype: "File",
				name: fileName,
			},
			auto: true,
		})
	}

	/**
	 * Get files attached to a document
	 * @param {string} doctype - Parent DocType
	 * @param {string} docname - Parent document name
	 * @returns {Object} Frappe resource
	 */
	getAttachedFiles(doctype, docname) {
		return apiClient.createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "File",
				filters: {
					attached_to_doctype: doctype,
					attached_to_name: docname,
				},
				fields: [
					"name",
					"file_name",
					"file_url",
					"file_size",
					"is_private",
					"creation",
				],
				order_by: "creation desc",
			},
			auto: true,
		})
	}

	/**
	 * Delete file
	 * @param {string} fileName - File document name
	 * @returns {Promise<void>}
	 */
	async deleteFile(fileName) {
		return apiClient.call("frappe.client.delete", {
			doctype: "File",
			name: fileName,
		})
	}

	/**
	 * Delete multiple files
	 * @param {Array<string>} fileNames - Array of file document names
	 * @returns {Promise<void>}
	 */
	async deleteMultipleFiles(fileNames) {
		const deletePromises = fileNames.map((fileName) =>
			this.deleteFile(fileName),
		)
		return Promise.all(deletePromises)
	}

	/**
	 * Get file URL
	 * @param {string} fileName - File document name or file URL
	 * @returns {string} Full file URL
	 */
	getFileURL(fileName) {
		if (fileName.startsWith("http://") || fileName.startsWith("https://")) {
			return fileName
		}
		if (fileName.startsWith("/files/")) {
			return window.location.origin + fileName
		}
		return (
			window.location.origin +
			"/api/method/frappe.utils.file_manager.get_file?file_url=" +
			fileName
		)
	}

	/**
	 * Download file
	 * @param {string} fileUrl - File URL
	 * @param {string} fileName - Suggested file name for download
	 */
	downloadFile(fileUrl, fileName = null) {
		const link = document.createElement("a")
		link.href = this.getFileURL(fileUrl)
		if (fileName) {
			link.download = fileName
		}
		link.target = "_blank"
		document.body.appendChild(link)
		link.click()
		document.body.removeChild(link)
	}

	/**
	 * Rename file
	 * @param {string} fileName - File document name
	 * @param {string} newName - New file name
	 * @returns {Promise<void>}
	 */
	async renameFile(fileName, newName) {
		return apiClient.call("frappe.client.rename_doc", {
			doctype: "File",
			old_name: fileName,
			new_name: newName,
		})
	}

	/**
	 * Update file metadata
	 * @param {string} fileName - File document name
	 * @param {Object} metadata - Metadata to update
	 * @returns {Promise<void>}
	 */
	async updateFileMetadata(fileName, metadata) {
		return apiClient.call("frappe.client.set_value", {
			doctype: "File",
			name: fileName,
			fieldname: metadata,
		})
	}

	/**
	 * Get file size in human-readable format
	 * @param {number} bytes - File size in bytes
	 * @returns {string} Human-readable file size
	 */
	formatFileSize(bytes) {
		if (bytes === 0) return "0 Bytes"

		const k = 1024
		const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
		const i = Math.floor(Math.log(bytes) / Math.log(k))

		return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
	}

	/**
	 * Validate file type
	 * @param {File} file - File object
	 * @param {Array<string>} allowedTypes - Allowed MIME types or extensions
	 * @returns {boolean} True if file type is allowed
	 */
	validateFileType(file, allowedTypes) {
		if (!allowedTypes || allowedTypes.length === 0) return true

		const fileExtension = "." + file.name.split(".").pop().toLowerCase()
		const fileMimeType = file.type.toLowerCase()

		return allowedTypes.some((type) => {
			if (type.startsWith(".")) {
				return fileExtension === type.toLowerCase()
			}
			return fileMimeType === type.toLowerCase()
		})
	}

	/**
	 * Validate file size
	 * @param {File} file - File object
	 * @param {number} maxSizeInMB - Maximum file size in MB
	 * @returns {boolean} True if file size is within limit
	 */
	validateFileSize(file, maxSizeInMB) {
		if (!maxSizeInMB) return true
		const maxSizeInBytes = maxSizeInMB * 1024 * 1024
		return file.size <= maxSizeInBytes
	}
}

export const documentService = new DocumentService()
