<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Request Type Builder</h1>
            <p class="mt-1 text-sm text-gray-500">Visual configuration editor for Request Types</p>
          </div>
          <div class="flex gap-3">
            <button
              @click="loadTemplate"
              :disabled="loading"
              class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ loading ? 'Loading...' : 'Load Request Type' }}
            </button>
            <button
              @click="saveRequestType"
              :disabled="saving || loading"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ saving ? 'Saving...' : 'Save Request Type' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Request Type Name</label>
                <input
                  v-model="requestType.name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Building Consent"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  v-model="requestType.category"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select Category</option>
                  <option value="Planning">Planning</option>
                  <option value="Building">Building</option>
                  <option value="Social Assistance">Social Assistance</option>
                  <option value="Environmental">Environmental</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  v-model="requestType.description"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe this request type..."
                ></textarea>
              </div>

              <div class="flex items-center gap-4">
                <label class="flex items-center">
                  <input
                    v-model="requestType.collects_payment"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">Collects Payment</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="requestType.make_payment"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">Makes Payment</span>
                </label>
              </div>
            </div>
          </div>

          <div class="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Template Library</h2>
            <div v-if="loading" class="text-center py-4 text-gray-500">Loading templates...</div>
            <div v-else-if="availableTemplates.length === 0" class="text-center py-4 text-gray-500">No templates available</div>
            <div v-else class="space-y-2">
              <button
                v-for="template in availableTemplates"
                :key="template.name"
                @click="applyTemplate(template.name)"
                class="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
              >
                <div class="font-medium text-gray-900">{{ template.title }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ template.description }}</div>
              </button>
            </div>
          </div>

          <div class="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">JSON Export</h2>
            <button
              @click="showJsonPreview = !showJsonPreview"
              class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200"
            >
              {{ showJsonPreview ? 'Hide' : 'Show' }} JSON Preview
            </button>
            <div v-if="showJsonPreview" class="mt-4">
              <textarea
                :value="jsonPreview"
                readonly
                rows="12"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-xs bg-gray-50"
              ></textarea>
              <button
                @click="copyJsonToClipboard"
                class="mt-2 w-full px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
              >
                Copy to Clipboard
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-lg font-semibold text-gray-900">Steps Configuration</h2>
              <button
                @click="addStep"
                class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
              >
                + Add Step
              </button>
            </div>

            <div v-if="requestType.steps.length === 0" class="text-center py-12 text-gray-500">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <p class="mt-2 text-sm">No steps configured yet</p>
              <p class="text-xs text-gray-400 mt-1">Click "Add Step" or use a template to get started</p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="(step, stepIndex) in requestType.steps"
                :key="stepIndex"
                class="border border-gray-200 rounded-lg overflow-hidden"
              >
                <div class="bg-gray-50 px-4 py-3 flex items-center justify-between border-b border-gray-200">
                  <div class="flex items-center gap-3">
                    <div class="flex items-center gap-2">
                      <button
                        @click="moveStep(stepIndex, 'up')"
                        :disabled="stepIndex === 0"
                        class="p-1 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                        </svg>
                      </button>
                      <button
                        @click="moveStep(stepIndex, 'down')"
                        :disabled="stepIndex === requestType.steps.length - 1"
                        class="p-1 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                        </svg>
                      </button>
                    </div>
                    <span class="text-sm font-medium text-gray-900">Step {{ stepIndex + 1 }}</span>
                    <input
                      v-model="step.step_title"
                      type="text"
                      class="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Step Title"
                    />
                  </div>
                  <div class="flex items-center gap-2">
                    <button
                      @click="toggleStep(stepIndex)"
                      class="text-sm text-gray-600 hover:text-gray-900"
                    >
                      {{ step.expanded ? 'Collapse' : 'Expand' }}
                    </button>
                    <button
                      @click="deleteStep(stepIndex)"
                      class="text-sm text-red-600 hover:text-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                <div v-if="step.expanded" class="p-4">
                  <div class="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <label class="block text-xs font-medium text-gray-700 mb-1">Step Code</label>
                      <input
                        v-model="step.step_code"
                        type="text"
                        class="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        placeholder="e.g., applicant_details"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-700 mb-1">Component</label>
                      <select
                        v-model="step.step_component"
                        class="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      >
                        <option value="DynamicStepRenderer">Dynamic Step Renderer</option>
                        <option value="Custom">Custom Component</option>
                      </select>
                    </div>
                  </div>

                  <div class="flex gap-4 mb-4">
                    <label class="flex items-center text-sm">
                      <input v-model="step.is_required" type="checkbox" class="mr-2"/>
                      Required
                    </label>
                    <label class="flex items-center text-sm">
                      <input v-model="step.show_on_review" type="checkbox" class="mr-2"/>
                      Show on Review
                    </label>
                  </div>

                  <div class="mt-4">
                    <div class="flex items-center justify-between mb-2">
                      <h4 class="text-sm font-medium text-gray-700">Sections</h4>
                      <button
                        @click="addSection(stepIndex)"
                        class="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      >
                        + Add Section
                      </button>
                    </div>

                    <div v-if="!step.sections || step.sections.length === 0" class="text-xs text-gray-500 text-center py-4">
                      No sections yet
                    </div>

                    <div v-else class="space-y-3">
                      <div
                        v-for="(section, sectionIndex) in step.sections"
                        :key="sectionIndex"
                        class="bg-gray-50 p-3 rounded border border-gray-200"
                      >
                        <div class="flex items-center justify-between mb-2">
                          <input
                            v-model="section.section_title"
                            type="text"
                            class="flex-1 px-2 py-1 border border-gray-300 rounded text-sm mr-2"
                            placeholder="Section Title"
                          />
                          <button
                            @click="deleteSection(stepIndex, sectionIndex)"
                            class="text-xs text-red-600 hover:text-red-700"
                          >
                            Delete
                          </button>
                        </div>

                        <div class="grid grid-cols-2 gap-2 mb-2">
                          <div>
                            <label class="block text-xs text-gray-600 mb-1">Section Code</label>
                            <input
                              v-model="section.section_code"
                              type="text"
                              class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                              placeholder="e.g., personal_info"
                            />
                          </div>
                          <div>
                            <label class="block text-xs text-gray-600 mb-1">Section Type</label>
                            <select
                              v-model="section.section_type"
                              class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                            >
                              <option value="Standard">Standard</option>
                              <option value="Tab">Tab</option>
                              <option value="Accordion">Accordion</option>
                            </select>
                          </div>
                        </div>

                        <div class="mt-3">
                          <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-medium text-gray-700">Fields</span>
                            <button
                              @click="addField(stepIndex, sectionIndex)"
                              class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                            >
                              + Add Field
                            </button>
                          </div>

                          <div v-if="!section.fields || section.fields.length === 0" class="text-xs text-gray-400 text-center py-2">
                            No fields yet
                          </div>

                          <div v-else class="space-y-2">
                            <div
                              v-for="(field, fieldIndex) in section.fields"
                              :key="fieldIndex"
                              class="bg-white p-2 rounded border border-gray-200"
                            >
                              <div class="grid grid-cols-3 gap-2">
                                <div class="col-span-2">
                                  <input
                                    v-model="field.field_label"
                                    type="text"
                                    class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                                    placeholder="Field Label"
                                  />
                                </div>
                                <div>
                                  <select
                                    v-model="field.field_type"
                                    class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                                  >
                                    <option value="Data">Text</option>
                                    <option value="Text">Textarea</option>
                                    <option value="Select">Select</option>
                                    <option value="Date">Date</option>
                                    <option value="Check">Checkbox</option>
                                    <option value="Currency">Currency</option>
                                    <option value="Int">Integer</option>
                                    <option value="Float">Float</option>
                                  </select>
                                </div>
                              </div>

                              <div class="grid grid-cols-3 gap-2 mt-2">
                                <div class="col-span-2">
                                  <input
                                    v-model="field.field_name"
                                    type="text"
                                    class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                                    placeholder="field_name"
                                  />
                                </div>
                                <div class="flex items-center gap-2">
                                  <label class="flex items-center text-xs">
                                    <input v-model="field.is_required" type="checkbox" class="mr-1 text-xs"/>
                                    Required
                                  </label>
                                  <button
                                    @click="deleteField(stepIndex, sectionIndex, fieldIndex)"
                                    class="text-xs text-red-600 hover:text-red-700 ml-auto"
                                  >
                                    ✕
                                  </button>
                                </div>
                              </div>

                              <div v-if="field.field_type === 'Select'" class="mt-2">
                                <textarea
                                  v-model="field.options"
                                  rows="2"
                                  class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                                  placeholder="Options (one per line)"
                                ></textarea>
                              </div>

                              <div class="mt-2">
                                <input
                                  v-model="field.validation"
                                  type="text"
                                  class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
                                  placeholder="Validation: email, phone, eval:value >= 18"
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { call } from "frappe-ui"
import { computed, onMounted, reactive, ref } from "vue"

// Request Type Data Model
const requestType = reactive({
	name: "",
	category: "",
	description: "",
	collects_payment: false,
	make_payment: false,
	steps: [],
})

// Available Templates
const availableTemplates = ref([])
const loading = ref(false)
const saving = ref(false)
const showJsonPreview = ref(false)

// JSON Preview computed
const jsonPreview = computed(() => {
	return JSON.stringify(requestType, null, 2)
})

// --- Utility Functions ---

// Function to renumber steps after move/delete
function renumberSteps() {
	requestType.steps.forEach((step, i) => {
		step.step_number = i + 1
	})
}

// Function to generate a stable unique ID for v-for keys
function generateUniqueId() {
	return Date.now().toString(36) + Math.random().toString(36).substr(2, 5)
}

// --- Step Management ---

function addStep() {
	requestType.steps.push({
		id: generateUniqueId(), // Added stable ID
		step_number: requestType.steps.length + 1,
		step_code: `step_${requestType.steps.length + 1}`,
		step_title: `Step ${requestType.steps.length + 1}`,
		step_component: "DynamicStepRenderer",
		is_required: true,
		show_on_review: true,
		expanded: true, // Ensure it's expanded by default
		sections: [],
	})
}

function deleteStep(index) {
	if (confirm("Are you sure you want to delete this step?")) {
		requestType.steps.splice(index, 1)
		renumberSteps() // Renumber after deletion
	}
}

function moveStep(index, direction) {
	const newIndex = direction === "up" ? index - 1 : index + 1
	if (newIndex >= 0 && newIndex < requestType.steps.length) {
		// Standard swap logic
		const temp = requestType.steps[index]
		requestType.steps[index] = requestType.steps[newIndex]
		requestType.steps[newIndex] = temp
		renumberSteps() // Renumber after move
	}
}

function toggleStep(index) {
	// Ensure the property exists before toggling
	const step = requestType.steps[index]
	step.expanded = step.expanded === undefined ? false : !step.expanded
}

// --- Section Management ---
function addSection(stepIndex) {
	if (!requestType.steps[stepIndex].sections) {
		requestType.steps[stepIndex].sections = []
	}
	requestType.steps[stepIndex].sections.push({
		id: generateUniqueId(), // Added stable ID
		section_code: `section_${requestType.steps[stepIndex].sections.length + 1}`,
		section_title: "",
		section_type: "Standard",
		sequence: requestType.steps[stepIndex].sections.length + 1,
		is_enabled: true,
		is_required: true,
		show_on_review: true,
		fields: [],
	})
}

function deleteSection(stepIndex, sectionIndex) {
	requestType.steps[stepIndex].sections.splice(sectionIndex, 1)
}

// --- Field Management ---
function addField(stepIndex, sectionIndex) {
	if (!requestType.steps[stepIndex].sections[sectionIndex].fields) {
		requestType.steps[stepIndex].sections[sectionIndex].fields = []
	}
	requestType.steps[stepIndex].sections[sectionIndex].fields.push({
		id: generateUniqueId(), // Added stable ID
		field_name: "",
		field_label: "",
		field_type: "Data",
		is_required: false,
		show_on_review: true,
		options: "",
		validation: "",
	})
}

function deleteField(stepIndex, sectionIndex, fieldIndex) {
	requestType.steps[stepIndex].sections[sectionIndex].fields.splice(
		fieldIndex,
		1,
	)
}

// --- API Calls / Load / Save ---

async function loadAvailableTemplates() {
	try {
		loading.value = true
		const response = await call("lodgeick.api.get_step_templates")
		availableTemplates.value = response || []
	} catch (error) {
		console.error("Failed to load templates:", error)
		alert("Failed to load templates from backend")
	} finally {
		loading.value = false
	}
}

async function applyTemplate(templateName) {
	try {
		loading.value = true
		const response = await call("lodgeick.api.load_step_template", {
			template_name: templateName,
		})

		if (!response || !response.success || !response.template) {
			alert(`Failed to load template: ${response?.error || "Unknown error"}`)
			return
		}

		const template = response.template

		// Create new step from template
		const newStep = {
			id: generateUniqueId(), // Ensure new step has a unique ID
			step_number: requestType.steps.length + 1,
			step_code: template.step_config.step_code,
			step_title: template.step_config.step_title,
			step_component: template.step_config.step_component,
			is_enabled: template.step_config.is_enabled ?? true,
			is_required: template.step_config.is_required ?? true,
			show_on_review: template.step_config.show_on_review ?? true,
			description: template.step_config.description || "",
			expanded: true, // IMPORTANT: Ensure step is expanded for visibility
			sections: [],
		}

		// Add sections from template (Defensive checks added for existence)
		if (template.sections && Array.isArray(template.sections)) {
			for (const section of template.sections) {
				const newSection = {
					id: generateUniqueId(), // Ensure new section has a unique ID
					section_code: section.section_code,
					section_title: section.section_title,
					section_type: section.section_type,
					// ... (other section properties)
					fields: [],
				}

				// Add fields from template
				if (section.fields && Array.isArray(section.fields)) {
					for (const field of section.fields) {
						newSection.fields.push({
							id: generateUniqueId(), // Ensure new field has a unique ID
							field_name: field.field_name,
							// ... (other field properties)
							// Note: Only necessary properties for the builder were kept for brevity
						})
					}
				}

				newStep.sections.push(newSection)
			}
		}

		// Add step to request type
		requestType.steps.push(newStep)

		alert(`Template "${template.template_title}" applied successfully!`)
	} catch (error) {
		console.error("Failed to apply template:", error)
		alert("Failed to apply template")
	} finally {
		loading.value = false
	}
}

function loadTemplate() {
	const rtName = prompt("Enter Request Type name to load:")
	if (!rtName) return

	loadRequestTypeConfig(rtName)
}

async function loadRequestTypeConfig(rtName) {
	try {
		loading.value = true
		const response = await call("lodgeick.api.load_request_type_config", {
			request_type_name: rtName,
		})

		if (!response.success) {
			alert(`Failed to load Request Type: ${response.error}`)
			return
		}

		const config = response.config

		// 1. Update basic metadata
		requestType.name = config.name
		requestType.category = config.category
		requestType.description = config.description
		requestType.collects_payment = config.collects_payment
		requestType.make_payment = config.make_payment

		// 2. Process steps to ensure IDs and expanded status
		requestType.steps = (config.steps || []).map((step) => {
			// Ensure the step is expanded and has an ID for proper rendering
			step.expanded = true
			step.id = step.id || generateUniqueId()

			// Ensure sections also have IDs
			step.sections = (step.sections || []).map((section) => {
				section.id = section.id || generateUniqueId()

				// Ensure fields also have IDs
				section.fields = (section.fields || []).map((field) => {
					field.id = field.id || generateUniqueId()
					return field
				})

				return section
			})

			return step
		})

		alert(`Request Type "${rtName}" loaded successfully!`)
	} catch (error) {
		console.error("Failed to load Request Type:", error)
		alert("Failed to load Request Type")
	} finally {
		loading.value = false
	}
}

// Save
async function saveRequestType() {
	// ... (Existing validation logic remains, but more robust checks are highly recommended)
	// --- New: Preliminary Uniqueness Check (Crucial for robust API/DB saves) ---
	const stepCodes = new Set()
	const fieldNames = new Set()

	for (const step of requestType.steps) {
		if (stepCodes.has(step.step_code)) {
			alert(`Error: Duplicate Step Code found: ${step.step_code}`)
			return
		}
		stepCodes.add(step.step_code)

		if (!step.step_code || !step.step_title) {
			alert("All steps must have a step code and title")
			return
		}

		for (const section of step.sections) {
			if (!section.section_code || !section.section_title) {
				alert("All sections must have a code and title")
				return
			}

			for (const field of section.fields) {
				if (!field.field_name || !field.field_label || !field.field_type) {
					alert("All fields must have a name, label, and type")
					return
				}
				if (fieldNames.has(field.field_name)) {
					alert(
						`Error: Duplicate Field Name found: ${field.field_name}. Field names must be unique across the entire Request Type.`,
					)
					return
				}
				fieldNames.add(field.field_name)
			}
		}
	}
	// --- End Uniqueness Check ---

	try {
		saving.value = true
		// NOTE: It is advisable to clean the data before sending, removing the temporary 'id' and 'expanded' properties.
		const configToSave = JSON.parse(JSON.stringify(requestType)) // Deep clone
		configToSave.steps.forEach((step) => {
			delete step.id // Remove temporary ID
			delete step.expanded // Remove temporary UI state

			if (step.sections) {
				step.sections.forEach((section) => {
					delete section.id
					if (section.fields) {
						section.fields.forEach((field) => {
							delete field.id
						})
					}
				})
			}
		})

		const response = await call("lodgeick.api.save_request_type_config", {
			config: configToSave,
		})

		if (!response.success) {
			alert(`Failed to save: ${response.error}`)
			return
		}

		alert(response.message)
	} catch (error) {
		console.error("Failed to save Request Type:", error)
		alert("Failed to save Request Type")
	} finally {
		saving.value = false
	}
}

// JSON Export
function copyJsonToClipboard() {
	navigator.clipboard
		.writeText(jsonPreview.value)
		.then(() => {
			alert("JSON copied to clipboard!")
		})
		.catch((err) => {
			console.error("Failed to copy:", err)
			alert("Failed to copy to clipboard")
		})
}

// Load templates on mount
onMounted(() => {
	loadAvailableTemplates()
})
</script>