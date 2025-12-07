<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
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
              class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Load Template
            </button>
            <button
              @click="saveRequestType"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
            >
              Save Request Type
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Panel: Request Type Metadata -->
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

          <!-- Template Library -->
          <div class="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Template Library</h2>
            <div class="space-y-2">
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
        </div>

        <!-- Center Panel: Step Configuration -->
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

            <!-- Steps List -->
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
                <!-- Step Header -->
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

                <!-- Step Body (Expandable) -->
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

                  <!-- Sections -->
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

                        <!-- Fields -->
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
import { ref, reactive } from 'vue'

// Request Type Data Model
const requestType = reactive({
  name: '',
  category: '',
  description: '',
  collects_payment: false,
  make_payment: false,
  steps: []
})

// Available Templates
const availableTemplates = ref([
  {
    name: 'declaration',
    title: 'Declaration & Submission',
    description: 'Standard declaration with signature (5 fields)'
  },
  {
    name: 'applicant_details',
    title: 'Applicant Details',
    description: 'Personal info and address (7 fields)'
  },
  {
    name: 'bank_details',
    title: 'Bank Account Details',
    description: 'For payouts to applicants (5 fields)'
  },
  {
    name: 'payment_collection',
    title: 'Payment & Invoice',
    description: 'For fee collection from applicants (6 fields)'
  }
])

// Step Management
function addStep() {
  requestType.steps.push({
    step_number: requestType.steps.length + 1,
    step_code: `step_${requestType.steps.length + 1}`,
    step_title: `Step ${requestType.steps.length + 1}`,
    step_component: 'DynamicStepRenderer',
    is_required: true,
    show_on_review: true,
    expanded: true,
    sections: []
  })
}

function deleteStep(index) {
  if (confirm('Delete this step?')) {
    requestType.steps.splice(index, 1)
    // Renumber steps
    requestType.steps.forEach((step, i) => {
      step.step_number = i + 1
    })
  }
}

function moveStep(index, direction) {
  const newIndex = direction === 'up' ? index - 1 : index + 1
  if (newIndex >= 0 && newIndex < requestType.steps.length) {
    const temp = requestType.steps[index]
    requestType.steps[index] = requestType.steps[newIndex]
    requestType.steps[newIndex] = temp
    // Renumber
    requestType.steps.forEach((step, i) => {
      step.step_number = i + 1
    })
  }
}

function toggleStep(index) {
  requestType.steps[index].expanded = !requestType.steps[index].expanded
}

// Section Management
function addSection(stepIndex) {
  if (!requestType.steps[stepIndex].sections) {
    requestType.steps[stepIndex].sections = []
  }
  requestType.steps[stepIndex].sections.push({
    section_code: `section_${requestType.steps[stepIndex].sections.length + 1}`,
    section_title: '',
    section_type: 'Standard',
    sequence: requestType.steps[stepIndex].sections.length + 1,
    is_enabled: true,
    is_required: true,
    show_on_review: true,
    fields: []
  })
}

function deleteSection(stepIndex, sectionIndex) {
  requestType.steps[stepIndex].sections.splice(sectionIndex, 1)
}

// Field Management
function addField(stepIndex, sectionIndex) {
  if (!requestType.steps[stepIndex].sections[sectionIndex].fields) {
    requestType.steps[stepIndex].sections[sectionIndex].fields = []
  }
  requestType.steps[stepIndex].sections[sectionIndex].fields.push({
    field_name: '',
    field_label: '',
    field_type: 'Data',
    is_required: false,
    show_on_review: true,
    options: '',
    validation: ''
  })
}

function deleteField(stepIndex, sectionIndex, fieldIndex) {
  requestType.steps[stepIndex].sections[sectionIndex].fields.splice(fieldIndex, 1)
}

// Template Application
async function applyTemplate(templateName) {
  // TODO: Load template from backend and apply to requestType
  alert(`Applying template: ${templateName}`)
}

function loadTemplate() {
  // TODO: Show modal to select and load existing Request Type
  alert('Load Template modal - TODO')
}

// Save
async function saveRequestType() {
  if (!requestType.name) {
    alert('Please enter a Request Type name')
    return
  }

  console.log('Saving Request Type:', requestType)
  alert('Request Type saved! (TODO: Implement backend save)')
}
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
