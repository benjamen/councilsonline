<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Proposed Conditions</h2>
    <p class="text-gray-600 mb-8">Suggest conditions that could be imposed to address adverse effects</p>

    <div class="space-y-6">
      <!-- Info Box -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">About Proposed Conditions</h5>
            <p class="text-blue-800 text-sm mt-1">
              Proposing consent conditions demonstrates a proactive approach to managing effects.
              Conditions should be specific, measurable, achievable, and directly related to managing adverse effects.
            </p>
          </div>
        </div>
      </div>

      <!-- Template Selection (Optional) -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">Select from Standard Conditions</h3>
            <p class="text-sm text-gray-600 mt-1">Choose from pre-approved condition templates or create your own</p>
          </div>
          <button
            @click="showTemplates = !showTemplates"
            type="button"
            class="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium text-sm border border-blue-600 rounded-lg hover:bg-blue-50"
          >
            {{ showTemplates ? 'Hide Templates' : 'Browse Templates' }}
          </button>
        </div>

        <!-- Template Browser -->
        <div v-if="showTemplates" class="mt-4 border-t border-gray-200 pt-4">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Category</label>
            <select
              v-model="selectedCategory"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="All">All Categories</option>
              <option value="General">General</option>
              <option value="Timing">Timing</option>
              <option value="Lapse">Lapse</option>
              <option value="Environmental Management">Environmental Management</option>
              <option value="Construction">Construction</option>
              <option value="Operation">Operation</option>
              <option value="Landscape">Landscape</option>
              <option value="Ecology">Ecology</option>
              <option value="Traffic">Traffic</option>
              <option value="Noise">Noise</option>
              <option value="Discharge">Discharge</option>
              <option value="Earthworks">Earthworks</option>
              <option value="Water">Water</option>
              <option value="Coastal">Coastal</option>
            </select>
          </div>

          <!-- Template List -->
          <div v-if="loadingTemplates" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
            <p class="text-sm text-gray-600">Loading templates...</p>
          </div>

          <div v-else-if="filteredTemplates.length === 0" class="text-center py-8 text-gray-500">
            <p class="text-sm">No templates found for this category</p>
          </div>

          <div v-else class="space-y-2 max-h-96 overflow-y-auto">
            <div
              v-for="template in filteredTemplates"
              :key="template.name"
              @click="addConditionFromTemplate(template)"
              class="border border-gray-200 rounded-lg p-4 hover:border-blue-600 hover:bg-blue-50 cursor-pointer transition-all"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-medium text-gray-900">{{ template.template_name }}</h4>
                    <span v-if="template.condition_code" class="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                      {{ template.condition_code }}
                    </span>
                    <span class="text-xs text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
                      {{ template.condition_category }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-700">{{ template.condition_text }}</p>
                  <p v-if="template.timing" class="text-xs text-gray-500 mt-1">
                    ⏱ Timing: {{ template.timing }}
                  </p>
                </div>
                <button
                  class="ml-4 text-blue-600 hover:text-blue-700 text-sm font-medium whitespace-nowrap"
                >
                  + Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Proposed Conditions Section -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-900">Your Proposed Conditions</h3>
            <button
              @click="addCondition"
              type="button"
              class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Add Custom Condition
            </button>
          </div>
        </div>

        <div class="p-6">
          <div v-if="localData.proposed_conditions && localData.proposed_conditions.length > 0" class="space-y-4">
            <div
              v-for="(condition, index) in localData.proposed_conditions"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <div class="flex justify-between items-start mb-4">
                <h4 class="font-medium text-gray-900">Condition {{ index + 1 }}</h4>
                <button
                  @click="removeCondition(index)"
                  type="button"
                  class="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Remove
                </button>
              </div>

              <div class="grid md:grid-cols-2 gap-4 mb-4">
                <!-- Condition Category -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Condition Category
                  </label>
                  <select
                    v-model="condition.category"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select category...</option>
                    <option value="General">General</option>
                    <option value="Construction">Construction Management</option>
                    <option value="Operational">Operational</option>
                    <option value="Landscaping">Landscaping</option>
                    <option value="Servicing">Servicing & Infrastructure</option>
                    <option value="Traffic">Traffic & Parking</option>
                    <option value="Noise">Noise</option>
                    <option value="Stormwater">Stormwater</option>
                    <option value="Contamination">Contamination</option>
                    <option value="Heritage">Heritage</option>
                    <option value="Ecology">Ecology & Biodiversity</option>
                    <option value="Monitoring">Monitoring & Reporting</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <!-- Timing -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Timing
                  </label>
                  <select
                    v-model="condition.timing"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select timing...</option>
                    <option value="Prior to Commencement">Prior to Commencement</option>
                    <option value="During Construction">During Construction</option>
                    <option value="Prior to Occupation">Prior to Occupation</option>
                    <option value="Ongoing">Ongoing</option>
                    <option value="On Completion">On Completion</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <!-- Condition Text -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Condition Wording <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="condition.condition_text"
                  required
                  rows="4"
                  placeholder="Write the proposed condition in clear, enforceable language...

Example: 'All construction activities shall be limited to the hours of 7:00am to 7:00pm Monday to Saturday, with no work permitted on Sundays or public holidays.'"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>

              <!-- Rationale -->
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Rationale
                </label>
                <textarea
                  v-model="condition.rationale"
                  rows="3"
                  placeholder="Explain the purpose of this condition and how it addresses adverse effects..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No conditions proposed yet</p>
            <p class="text-sm text-gray-500">Click "Add Condition" to propose consent conditions</p>
          </div>
        </div>
      </div>

      <!-- Example Conditions -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Example Condition Types</h3>
        </div>

        <div class="p-6 space-y-3">
          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Construction Hours</p>
            <p class="text-xs text-gray-600 mt-1">Limiting construction activities to specific hours to manage noise effects</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Landscaping</p>
            <p class="text-xs text-gray-600 mt-1">Requiring planting to screen development or enhance visual amenity</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Traffic Management</p>
            <p class="text-xs text-gray-600 mt-1">Requiring traffic management plans or parking arrangements</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Stormwater</p>
            <p class="text-xs text-gray-600 mt-1">Requiring stormwater management devices or erosion control measures</p>
          </div>

          <div class="border-l-4 border-blue-600 pl-4 py-2 bg-blue-50">
            <p class="font-medium text-sm text-gray-900">Monitoring</p>
            <p class="text-xs text-gray-600 mt-1">Requiring monitoring and reporting of environmental effects</p>
          </div>
        </div>
      </div>

      <!-- Guidance -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Writing Good Conditions</h5>
            <ul class="text-yellow-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li><strong>Clear:</strong> Unambiguous and easy to understand</li>
              <li><strong>Enforceable:</strong> Able to be monitored and enforced by the council</li>
              <li><strong>Necessary:</strong> Directly related to managing an identified adverse effect</li>
              <li><strong>Reasonable:</strong> Practical and achievable to implement</li>
              <li><strong>Specific:</strong> Include measurable standards, timeframes, or thresholds</li>
              <li>Note: The council may modify, add, or remove conditions during processing</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import { computed, defineEmits, defineProps, onMounted, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

// Template state
const showTemplates = ref(false)
const loadingTemplates = ref(false)
const availableTemplates = ref([])
const selectedCategory = ref("All")

// Create local copy of data
const localData = ref({
	proposed_conditions: props.modelValue.proposed_conditions || [],
})

// Watch for external changes
watch(
	() => props.modelValue.proposed_conditions,
	(newVal) => {
		if (newVal !== localData.value.proposed_conditions) {
			localData.value.proposed_conditions = newVal || []
		}
	},
	{ deep: true },
)

// Watch local changes and emit
watch(
	localData,
	(newVal) => {
		emit("update:modelValue", {
			...props.modelValue,
			proposed_conditions: newVal.proposed_conditions,
		})
	},
	{ deep: true },
)

// Filtered templates based on category and consent types
const filteredTemplates = computed(() => {
	let templates = availableTemplates.value

	// Filter by category
	if (selectedCategory.value !== "All") {
		templates = templates.filter(
			(t) => t.condition_category === selectedCategory.value,
		)
	}

	// Filter by consent types (if selected)
	const consentTypes =
		props.modelValue.consent_types?.map((ct) => ct.consent_type) || []
	if (consentTypes.length > 0) {
		templates = templates.filter((t) => {
			// Include if template applies to 'All' or matches one of the selected consent types
			return (
				t.applies_to_consent_types === "All" ||
				consentTypes.includes(t.applies_to_consent_types)
			)
		})
	}

	return templates
})

// Load templates when component mounts or when templates section is shown
watch(showTemplates, async (isShown) => {
	if (isShown && availableTemplates.value.length === 0) {
		await loadTemplates()
	}
})

const loadTemplates = async () => {
	loadingTemplates.value = true
	try {
		const result = await call("frappe.client.get_list", {
			doctype: "Consent Condition Template",
			fields: [
				"name",
				"template_name",
				"condition_code",
				"condition_category",
				"condition_text",
				"timing",
				"applies_to_consent_types",
				"is_standard",
			],
			filters: {
				is_active: 1,
			},
			limit_page_length: 100,
			order_by: "condition_category asc, template_name asc",
		})
		availableTemplates.value = result || []
	} catch (error) {
		console.error("[Step15] Error loading templates:", error)
		availableTemplates.value = []
	} finally {
		loadingTemplates.value = false
	}
}

const addConditionFromTemplate = (template) => {
	localData.value.proposed_conditions.push({
		category: template.condition_category,
		timing: template.timing || "",
		condition_text: template.condition_text,
		rationale: template.is_standard ? "Standard condition template" : "",
		template_name: template.template_name,
		condition_code: template.condition_code || "",
	})
}

const addCondition = () => {
	localData.value.proposed_conditions.push({
		category: "",
		timing: "",
		condition_text: "",
		rationale: "",
	})
}

const removeCondition = (index) => {
	localData.value.proposed_conditions.splice(index, 1)
}
</script>
