<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Assessment Template Builder</h1>
            <p class="mt-1 text-sm text-gray-500">Visual configuration editor for Assessment Templates</p>
          </div>
          <div class="flex gap-3">
            <button
              @click="showLoadDialog = true"
              :disabled="loading"
              class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ loading ? 'Loading...' : 'Load Template' }}
            </button>
            <button
              @click="saveTemplate"
              :disabled="saving || loading"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ saving ? 'Saving...' : 'Save Template' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Left Sidebar -->
        <div class="lg:col-span-1 space-y-6">

          <!-- Basic Information -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
                <input
                  v-model="template.template_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Resource Consent - Standard"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Request Type</label>
                <select
                  v-model="template.request_type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select Request Type</option>
                  <option v-for="rt in requestTypes" :key="rt.name" :value="rt.name">
                    {{ rt.type_name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Default Budget Hours</label>
                <input
                  v-model.number="template.default_budget_hours"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="40"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  v-model="template.description"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe this template..."
                ></textarea>
              </div>

              <div class="flex items-center">
                <input
                  v-model="template.is_active"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label class="ml-2 text-sm text-gray-700">Is Active</label>
              </div>
            </div>
          </div>

          <!-- Template Library -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Template Library</h2>

            <div v-if="loadingLibrary" class="text-center py-4 text-gray-500">
              Loading templates...
            </div>

            <div v-else-if="templateLibrary.length === 0" class="text-center py-4 text-gray-500">
              No templates available
            </div>

            <div v-else class="space-y-2">
              <button
                v-for="libTemplate in templateLibrary"
                :key="libTemplate.name"
                @click="loadFromLibrary(libTemplate.name)"
                class="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <div class="font-medium text-gray-900">{{ libTemplate.template_name }}</div>
                <div class="text-xs text-gray-500 mt-1">
                  {{ libTemplate.stage_count }} stages · {{ libTemplate.default_budget_hours }}h budget
                </div>
              </button>
            </div>
          </div>

          <!-- JSON Export/Import -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">JSON Export/Import</h2>

            <div class="space-y-3">
              <button
                @click="exportJSON"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Export JSON
              </button>

              <button
                @click="showImportDialog = true"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Import JSON
              </button>
            </div>
          </div>
        </div>

        <!-- Main Content: Stage Configuration -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-lg font-semibold text-gray-900">Assessment Stages</h2>
              <button
                @click="addStage"
                class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
              >
                + Add Stage
              </button>
            </div>

            <!-- Stages List -->
            <div v-if="template.stages.length === 0" class="text-center py-12 text-gray-500">
              <p>No stages configured yet.</p>
              <p class="text-sm mt-2">Click "Add Stage" to get started.</p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="(stage, index) in template.stages"
                :key="index"
                class="border border-gray-200 rounded-lg"
              >
                <!-- Stage Header -->
                <div class="bg-gray-50 px-4 py-3 flex items-center justify-between cursor-pointer"
                  @click="toggleStage(index)"
                >
                  <div class="flex items-center gap-3">
                    <span class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-semibold text-sm">
                      {{ stage.stage_number }}
                    </span>
                    <div>
                      <div class="font-medium text-gray-900">
                        {{ getStageTypeName(stage.stage_type) || 'Unnamed Stage' }}
                      </div>
                      <div class="text-xs text-gray-500">
                        {{ stage.estimated_hours || 0 }}h estimated
                        {{ stage.required ? '· Required' : '· Optional' }}
                      </div>
                    </div>
                  </div>

                  <div class="flex items-center gap-2">
                    <button
                      v-if="index > 0"
                      @click.stop="moveStageUp(index)"
                      class="p-1 text-gray-400 hover:text-gray-600"
                      title="Move Up"
                    >
                      ↑
                    </button>
                    <button
                      v-if="index < template.stages.length - 1"
                      @click.stop="moveStageDown(index)"
                      class="p-1 text-gray-400 hover:text-gray-600"
                      title="Move Down"
                    >
                      ↓
                    </button>
                    <button
                      @click.stop="deleteStage(index)"
                      class="p-1 text-red-400 hover:text-red-600"
                      title="Delete"
                    >
                      ✕
                    </button>
                    <span class="text-gray-400">
                      {{ expandedStages[index] ? '▼' : '▶' }}
                    </span>
                  </div>
                </div>

                <!-- Stage Content (Expandable) -->
                <div v-show="expandedStages[index]" class="p-4 space-y-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Stage Type</label>
                      <select
                        v-model="stage.stage_type"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Select Stage Type</option>
                        <option v-for="st in stageTypes" :key="st.name" :value="st.name">
                          {{ st.stage_type_name }}
                        </option>
                      </select>
                      <p v-if="stage.stage_type" class="mt-1 text-xs text-gray-500">
                        {{ getStageTypeDescription(stage.stage_type) }}
                      </p>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Estimated Hours</label>
                      <input
                        v-model.number="stage.estimated_hours"
                        type="number"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="8"
                      />
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                      v-model="stage.description"
                      rows="2"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Optional description for this stage..."
                    ></textarea>
                  </div>

                  <div class="flex items-center">
                    <input
                      v-model="stage.required"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label class="ml-2 text-sm text-gray-700">Required Stage</label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Load Template Dialog -->
    <div v-if="showLoadDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold mb-4">Load Template</h3>

        <div v-if="loadingLibrary" class="text-center py-4 text-gray-500">
          Loading templates...
        </div>

        <div v-else class="space-y-2 max-h-96 overflow-y-auto">
          <button
            v-for="libTemplate in templateLibrary"
            :key="libTemplate.name"
            @click="loadTemplate(libTemplate.name)"
            class="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50"
          >
            <div class="font-medium text-gray-900">{{ libTemplate.template_name }}</div>
            <div class="text-xs text-gray-500 mt-1">
              {{ libTemplate.request_type_name || 'No request type' }} · {{ libTemplate.stage_count }} stages
            </div>
          </button>
        </div>

        <div class="mt-4 flex justify-end gap-2">
          <button
            @click="showLoadDialog = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Import JSON Dialog -->
    <div v-if="showImportDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <h3 class="text-lg font-semibold mb-4">Import JSON</h3>

        <textarea
          v-model="importJSON"
          rows="12"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
          placeholder="Paste JSON configuration here..."
        ></textarea>

        <div class="mt-4 flex justify-end gap-2">
          <button
            @click="showImportDialog = false; importJSON = ''"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="importFromJSON"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            Import
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'

const router = useRouter()

// State
const loading = ref(false)
const saving = ref(false)
const loadingLibrary = ref(false)
const showLoadDialog = ref(false)
const showImportDialog = ref(false)
const importJSON = ref('')

const template = reactive({
  name: '',
  template_name: '',
  request_type: '',
  is_active: 1,
  default_budget_hours: null,
  description: '',
  stages: []
})

const templateLibrary = ref([])
const requestTypes = ref([])
const stageTypes = ref([])
const expandedStages = ref({})

// Load initial data
onMounted(async () => {
  await loadRequestTypes()
  await loadStageTypes()
  await loadTemplateLibrary()

  // Expand all stages by default
  expandAllStages()
})

async function loadRequestTypes() {
  try {
    const response = await call('frappe.client.get_list', {
      doctype: 'Request Type',
      fields: ['name', 'type_name'],
      filters: { is_active: 1 },
      order_by: 'type_name'
    })
    requestTypes.value = response
  } catch (error) {
    console.error('Failed to load request types:', error)
  }
}

async function loadStageTypes() {
  try {
    const response = await call('lodgeick.api.get_assessment_stage_types')
    if (response.success) {
      stageTypes.value = response.stage_types
    }
  } catch (error) {
    console.error('Failed to load stage types:', error)
  }
}

async function loadTemplateLibrary() {
  loadingLibrary.value = true
  try {
    const response = await call('lodgeick.api.get_assessment_templates')
    if (response.success) {
      templateLibrary.value = response.templates
    }
  } catch (error) {
    console.error('Failed to load template library:', error)
  } finally {
    loadingLibrary.value = false
  }
}

async function loadTemplate(templateName) {
  loading.value = true
  try {
    const response = await call('lodgeick.api.load_assessment_template', {
      template_name: templateName
    })

    if (response.success) {
      Object.assign(template, response.template)
      expandAllStages()
      showLoadDialog.value = false
    }
  } catch (error) {
    console.error('Failed to load template:', error)
    alert('Failed to load template: ' + error.message)
  } finally {
    loading.value = false
  }
}

async function loadFromLibrary(templateName) {
  await loadTemplate(templateName)
}

async function saveTemplate() {
  // Validation
  if (!template.template_name) {
    alert('Please enter a template name')
    return
  }

  if (template.stages.length === 0) {
    alert('Please add at least one stage')
    return
  }

  // Validate at least one required stage
  const hasRequiredStage = template.stages.some(s => s.required)
  if (!hasRequiredStage) {
    alert('At least one stage must be marked as required')
    return
  }

  saving.value = true
  try {
    const response = await call('lodgeick.api.save_assessment_template', {
      config: template
    })

    if (response.success) {
      alert('Template saved successfully!')
      template.name = response.template_name
      await loadTemplateLibrary()
    } else {
      alert('Failed to save template: ' + response.error)
    }
  } catch (error) {
    console.error('Failed to save template:', error)
    alert('Failed to save template: ' + error.message)
  } finally {
    saving.value = false
  }
}

function addStage() {
  const newStageNumber = template.stages.length + 1
  template.stages.push({
    stage_number: newStageNumber,
    stage_type: '',
    estimated_hours: null,
    required: 0,
    description: ''
  })

  // Expand the new stage
  expandedStages.value[template.stages.length - 1] = true
}

function deleteStage(index) {
  if (confirm('Are you sure you want to delete this stage?')) {
    template.stages.splice(index, 1)
    renumberStages()
  }
}

function moveStageUp(index) {
  if (index > 0) {
    const temp = template.stages[index]
    template.stages[index] = template.stages[index - 1]
    template.stages[index - 1] = temp
    renumberStages()
  }
}

function moveStageDown(index) {
  if (index < template.stages.length - 1) {
    const temp = template.stages[index]
    template.stages[index] = template.stages[index + 1]
    template.stages[index + 1] = temp
    renumberStages()
  }
}

function renumberStages() {
  template.stages.forEach((stage, index) => {
    stage.stage_number = index + 1
  })
}

function toggleStage(index) {
  expandedStages.value[index] = !expandedStages.value[index]
}

function expandAllStages() {
  template.stages.forEach((_, index) => {
    expandedStages.value[index] = true
  })
}

function getStageTypeName(stageType) {
  const st = stageTypes.value.find(s => s.name === stageType)
  return st ? st.stage_type_name : ''
}

function getStageTypeDescription(stageType) {
  const st = stageTypes.value.find(s => s.name === stageType)
  return st ? st.description?.replace(/<[^>]*>/g, '') : ''
}

function exportJSON() {
  const json = JSON.stringify(template, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${template.template_name || 'template'}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function importFromJSON() {
  try {
    const imported = JSON.parse(importJSON.value)
    Object.assign(template, imported)
    expandAllStages()
    showImportDialog.value = false
    importJSON.value = ''
    alert('Template imported successfully!')
  } catch (error) {
    alert('Invalid JSON: ' + error.message)
  }
}
</script>
