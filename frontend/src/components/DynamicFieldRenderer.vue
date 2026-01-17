<template>
  <div class="space-y-6">
    <div v-for="field in visibleFields" :key="field.field_name" class="field-wrapper">
      <!-- Property Address Selector (special handling for address fields) -->
      <div v-if="isAddressField(field)" class="form-group">
        <PropertyAddressSelector
          v-model="localData[field.field_name]"
          :label="field.field_label"
          :required="Boolean(field.is_required)"
        />
      </div>

      <!-- Data / Text Input -->
      <TextField
        v-else-if="field.field_type === 'Data'"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        :placeholder="getPlaceholder(field)"
        :icon="getFieldIcon(field)"
        @validate="handleFieldValidation(field)"
      />

      <!-- Select Dropdown -->
      <SelectField
        v-else-if="field.field_type === 'Select'"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        :options="getSelectOptions(field.options)"
        @validate="handleFieldValidation(field)"
      />

      <!-- Checkbox -->
      <CheckboxField
        v-else-if="field.field_type === 'Check'"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        @validate="handleFieldValidation(field)"
      />

      <!-- Text / Textarea / Text Editor / Small Text / Long Text -->
      <TextareaField
        v-else-if="['Text', 'Text Editor', 'Small Text', 'Long Text'].includes(field.field_type)"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        :placeholder="getPlaceholder(field)"
        @validate="handleFieldValidation(field)"
      />

      <!-- Date -->
      <DateField
        v-else-if="field.field_type === 'Date'"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        @validate="handleFieldValidation(field)"
      />

      <!-- Integer -->
      <NumberField
        v-else-if="field.field_type === 'Int'"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        :placeholder="getPlaceholder(field)"
        variant="int"
        @validate="handleFieldValidation(field)"
      />

      <!-- Float -->
      <NumberField
        v-else-if="field.field_type === 'Float'"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        :placeholder="getPlaceholder(field)"
        variant="float"
        @validate="handleFieldValidation(field)"
      />

      <!-- Currency -->
      <NumberField
        v-else-if="field.field_type === 'Currency'"
        :field="field"
        v-model="localData[field.field_name]"
        :validation-error="getValidationError(field.field_name)"
        variant="currency"
        @validate="handleFieldValidation(field)"
      />

      <!-- Attach / File Upload with Camera Support -->
      <div v-else-if="field.field_type === 'Attach' || field.field_type === 'Attach Image'" class="form-group">
        <CameraUpload
          :label="field.field_label"
          :required="field.is_required"
          :accept="field.field_type === 'Attach Image' ? 'image/*' : '*'"
          :multiple="false"
          :modelValue="getFileArray(field.field_name)"
          @update:modelValue="updateFileField(field.field_name, $event)"
          @upload="handleFileUploadToFrappe"
        />
      </div>

      <!-- Unsupported field type -->
      <div v-else class="form-group">
        <div class="text-sm text-gray-500 italic">
          Field type "{{ field.field_type }}" not yet supported for {{ field.field_label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import { isFieldVisible } from "../utils/conditionalLogic"
import { validateField } from "../utils/fieldValidation"
import CameraUpload from "./CameraUpload.vue"
import PhilippinesAddressInput from "./PhilippinesAddressInput.vue"
import PropertyAddressSelector from "./PropertyAddressSelector.vue"
import Tooltip from "./Tooltip.vue"
import CheckboxField from "./fields/CheckboxField.vue"
import DateField from "./fields/DateField.vue"
import NumberField from "./fields/NumberField.vue"
import SelectField from "./fields/SelectField.vue"
import TextField from "./fields/TextField.vue"
import TextareaField from "./fields/TextareaField.vue"

const props = defineProps({
	fields: {
		type: Array,
		required: true,
	},
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

const localData = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

// Filter visible fields based on depends_on logic
const visibleFields = computed(() => {
	return props.fields.filter((field) => {
		// Hide individual address component fields if Philippines Address Input is being used
		const parentSection = field.parent_section_code?.toLowerCase() || ""
		const addressSections = [
			"address",
			"residential_address",
			"permanent_address",
			"property_address",
			"current_address",
			"home_address",
		]
		const isInAddressSection = addressSections.includes(parentSection)
		const addressComponentFields = [
			"barangay",
			"municipality",
			"province",
			"city",
			"region",
			"zip_code",
			"postal_code",
		]

		// Check if this section has an address_line field (which triggers PhilippinesAddressInput)
		if (isInAddressSection) {
			const hasAddressLineField = props.fields.some(
				(f) =>
					f.parent_section_code === field.parent_section_code &&
					f.field_name === "address_line",
			)

			// If this section has address_line AND this field is one of the component fields, hide it
			if (
				hasAddressLineField &&
				addressComponentFields.includes(field.field_name)
			) {
				return false
			}
		}

		return isFieldVisible(field, localData.value)
	})
})

// Check if field is an address field
const isAddressField = (field) => {
	// Check if this is an address field that should use the PropertyAddressSelector
	const fieldName = field.field_name?.toLowerCase() || ""
	const fieldLabel = field.field_label?.toLowerCase() || ""
	const parentSection = field.parent_section_code?.toLowerCase() || ""

	// Address field indicators
	const addressFieldNames = [
		"address_line",
		"street",
		"residential_address",
		"property_address",
		"home_address",
		"current_address",
		"permanent_address",
	]
	const addressSections = [
		"address",
		"residential_address",
		"permanent_address",
		"property_address",
		"current_address",
		"home_address",
	]
	const addressLabels = [
		"residential address",
		"property address",
		"home address",
		"current address",
		"permanent address",
		"street / house number",
		"street address",
	]

	// Trigger PropertyAddressSelector if:
	// 1. Field name matches address patterns, OR
	// 2. Parent section is an address section and this is the first field (address_line or street), OR
	// 3. Field label indicates it's a main address field
	return (
		(addressFieldNames.includes(fieldName) && field.field_type === "Data") ||
		(addressSections.includes(parentSection) &&
			(fieldName === "address_line" || fieldName === "street") &&
			field.field_type === "Data") ||
		(addressLabels.some((label) => fieldLabel.includes(label)) &&
			field.field_type === "Data" &&
			!fieldLabel.includes("zip") &&
			!fieldLabel.includes("postal"))
	)
}

// Get placeholder text for field
const getPlaceholder = (field) => {
	if (field.placeholder) return field.placeholder

	// Generate smart placeholders based on field name/label
	const label = field.field_label?.toLowerCase() || ""

	if (label.includes("name")) return "e.g., Juan Dela Cruz"
	if (label.includes("email")) return "e.g., juan@example.com"
	if (
		label.includes("phone") ||
		label.includes("mobile") ||
		label.includes("contact")
	) {
		return "e.g., 0917 123 4567"
	}
	if (label.includes("age")) return "e.g., 25"
	if (label.includes("occupation")) return "e.g., Teacher"
	if (label.includes("income") || label.includes("salary")) return "e.g., 15000"

	return `Enter ${field.field_label}`
}

// Get icon for field based on type
const getFieldIcon = (field) => {
	const label = field.field_label?.toLowerCase() || ""

	if (label.includes("email")) {
		return '<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/></svg>'
	}
	if (
		label.includes("phone") ||
		label.includes("mobile") ||
		label.includes("contact")
	) {
		return '<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>'
	}
	if (label.includes("name")) {
		return '<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>'
	}

	return null
}

// Parse select options from newline-separated string
const getSelectOptions = (optionsString) => {
	if (!optionsString) return []
	return optionsString
		.split("\n")
		.map((opt) => opt.trim())
		.filter(Boolean)
}

// Use step validation composable
import { useStepValidation } from "../composables/useStepValidation"
const {
	errors: validationErrors,
	validateConfigField,
	clearFieldError,
} = useStepValidation()

// Validate a single field
const handleFieldValidation = (field) => {
	if (!field.validation && !field.is_required) {
		// Clear any existing error if no validation rule
		clearFieldError(field.field_name)
		return
	}

	const value = localData.value[field.field_name]
	validateConfigField(field.field_name, value, field, localData.value)
}

// Get validation error message for a field
const getValidationError = (fieldName) => {
	return validationErrors.value[fieldName] || ""
}

// Get file array for CameraUpload component (expects array)
const getFileArray = (fieldName) => {
	const value = localData.value[fieldName]
	// If it's already an array, return it
	if (Array.isArray(value)) return value
	// If it's undefined or null, return empty array
	if (!value) return []
	// If it's a string (file URL), convert to file object format
	if (typeof value === "string") {
		return [
			{
				file_url: value,
				name: value.split("/").pop(),
				preview: value,
			},
		]
	}
	return []
}

// Update file field when CameraUpload emits update
const updateFileField = (fieldName, fileArray) => {
	console.log(
		"[DynamicFieldRenderer] updateFileField called:",
		fieldName,
		fileArray,
	)

	// Immediately convert file array to URL string to avoid timing issues
	if (Array.isArray(fileArray) && fileArray.length > 0) {
		// Check if files have been uploaded (have file_url)
		const uploadedFiles = fileArray.filter((f) => f.file_url)
		if (uploadedFiles.length > 0) {
			// For single file uploads, store just the URL string
			const fileUrl = uploadedFiles[0].file_url
			console.log(
				"[DynamicFieldRenderer] Converting uploaded file to URL:",
				fileUrl,
			)
			localData.value[fieldName] = fileUrl
			return
		}
	}

	// Otherwise store the array as-is (files being uploaded)
	localData.value[fieldName] = fileArray
}

// Handle file upload to Frappe
const handleFileUploadToFrappe = async (fileData, resolveCallback) => {
	console.log(
		"[DynamicFieldRenderer] handleFileUploadToFrappe called with:",
		fileData,
	)

	try {
		console.log("[DynamicFieldRenderer] Starting file upload:", fileData.name)

		const formData = new FormData()
		formData.append("file", fileData.file)
		formData.append("is_private", "0")
		formData.append("folder", "Home/Attachments")

		console.log(
			"[DynamicFieldRenderer] Uploading to /api/method/upload_file...",
		)

		// Upload file to Frappe
		const response = await fetch("/api/method/upload_file", {
			method: "POST",
			credentials: "include",
			headers: {
				"X-Frappe-CSRF-Token": window.csrf_token,
			},
			body: formData,
		})

		console.log(
			"[DynamicFieldRenderer] Upload response status:",
			response.status,
		)

		if (!response.ok) {
			const errorText = await response.text()
			console.error("[DynamicFieldRenderer] Upload failed:", errorText)
			throw new Error(`Upload failed (${response.status}): ${errorText}`)
		}

		const result = await response.json()
		console.log("[DynamicFieldRenderer] Upload response:", result)

		if (result.message && result.message.file_url) {
			// Store the file URL in form data
			console.log(
				"[DynamicFieldRenderer] File uploaded successfully:",
				result.message.file_url,
			)

			// Update the file data with the uploaded URL
			fileData.file_url = result.message.file_url
			fileData.file_name = result.message.file_name

			console.log("[DynamicFieldRenderer] Updated fileData:", fileData)
		}

		// Resolve the upload promise to clear loading state
		console.log("[DynamicFieldRenderer] Calling resolveCallback()")
		resolveCallback()

		console.log("[DynamicFieldRenderer] File upload completed successfully")
	} catch (error) {
		console.error("[DynamicFieldRenderer] File upload error:", error)
		alert(`Failed to upload file: ${error.message}`)

		// Still resolve to clear loading state even on error
		console.log("[DynamicFieldRenderer] Calling resolveCallback() after error")
		resolveCallback()
	}
}

// Watch for file uploads and convert arrays to file URLs
watch(
	() => localData.value,
	(newData) => {
		// Convert file arrays to file URLs for storage
		Object.entries(newData).forEach(([key, value]) => {
			if (Array.isArray(value) && value.length > 0 && value[0].file_url) {
				// This is a file upload array with uploaded files
				// Extract just the file URLs for storage
				const fileUrls = value.map((f) => f.file_url).filter(Boolean)
				if (fileUrls.length > 0) {
					// For single file uploads, store just the URL string
					// For multiple files, store as array
					localData.value[key] = fileUrls.length === 1 ? fileUrls[0] : fileUrls
					console.log(
						`[DynamicFieldRenderer] Converted file array to URL for ${key}:`,
						localData.value[key],
					)
				}
			}
		})
	},
	{ deep: true },
)

// Set default values on mount
watch(
	() => props.fields,
	(fields) => {
		fields.forEach((field) => {
			if (field.default_value && !localData.value[field.field_name]) {
				if (field.default_value === "Today" && field.field_type === "Date") {
					localData.value[field.field_name] = new Date()
						.toISOString()
						.split("T")[0]
				} else {
					localData.value[field.field_name] = field.default_value
				}
			}
		})
	},
	{ immediate: true },
)
</script>

<style scoped>
.form-group {
  margin-bottom: 1.5rem;
}

input:focus, select:focus, textarea:focus {
  outline: none;
}

/* Remove default number input spinners for cleaner look */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* Ensure date input has proper cursor */
input[type="date"] {
  cursor: pointer;
}

/* Smooth transitions */
input, select, textarea {
  transition: all 0.2s ease-in-out;
}
</style>
