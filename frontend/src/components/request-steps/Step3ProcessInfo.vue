<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Council Process Information</h2>
    <p class="text-gray-600 mb-6">Understanding {{ councilName }}'s process for this application</p>

    <div v-if="requestTypeDetails" class="space-y-6">

      <!-- Council Meeting Section (if enabled) -->
      <div v-if="requestTypeDetails.council_meeting_available" class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Council Meeting</h3>
        <p class="text-sm text-gray-600 mb-4">
          You may schedule a Council Meeting with the Council to seek further clarifications in respect of your application before proceeding.
        </p>

        <div class="flex items-center gap-4 mb-4">
          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="preAppMeetingNotRequired"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span class="ml-2 text-sm text-gray-700">I do not require a council meeting</span>
          </label>
        </div>

        <button
          v-if="!preAppMeetingNotRequired"
          @click="openPreAppMeetingModal"
          type="button"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Request Council Meeting
        </button>

        <!-- Council Meeting List -->
        <div v-if="preAppMeetings && preAppMeetings.length > 0" class="mt-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">Requested Meetings</h4>
          <div class="space-y-2">
            <div
              v-for="(meeting, index) in preAppMeetings"
              :key="index"
              class="p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-start justify-between"
            >
              <div class="flex-1">
                <span class="text-sm font-medium text-gray-900">{{ meeting.meeting_type || 'Council Meeting' }}</span>
                <p class="text-xs text-gray-600 mt-1">{{ meeting.meeting_format }}</p>
                <p v-if="meeting.preferred_time_slot_1_start" class="text-xs text-gray-500 mt-1">
                  Preferred: {{ formatDate(meeting.preferred_time_slot_1_start) }}
                </p>
              </div>
              <button
                @click="removePreAppMeeting(index)"
                type="button"
                class="text-red-600 hover:text-red-800 text-sm ml-4"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-xl font-semibold text-gray-900">{{ requestTypeDetails.request_type_name }}</h3>
            <p v-if="requestTypeDetails.category" class="text-sm text-gray-500 mt-1">
              {{ requestTypeDetails.category }}
            </p>
          </div>
        </div>

        <div class="grid md:grid-cols-3 gap-4 mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div>
            <div class="text-xs text-blue-600 font-medium uppercase">Application Fee</div>
            <div class="text-2xl font-bold text-blue-900 mt-1">
              ${{ requestTypeDetails.base_fee || '0' }}
            </div>
            <div class="text-xs text-blue-600 mt-1">Plus any additional costs</div>
          </div>
          <div>
            <div class="text-xs text-blue-600 font-medium uppercase">Processing Time</div>
            <div class="text-2xl font-bold text-blue-900 mt-1">
              {{ requestTypeDetails.sla_days || 'N/A' }} <span class="text-base">days</span>
            </div>
            <div class="text-xs text-blue-600 mt-1">Standard timeframe</div>
          </div>
          <div>
            <div class="text-xs text-blue-600 font-medium uppercase">Payment Required</div>
            <div class="text-2xl font-bold text-blue-900 mt-1">
              {{ requestTypeDetails.requires_payment ? 'Yes' : 'No' }}
            </div>
            <div class="text-xs text-blue-600 mt-1">Before processing</div>
          </div>
        </div>
      </div>

      <div v-if="requestTypeDetails.process_description" class="bg-white border border-gray-200 rounded-lg p-6">
        <h4 class="text-lg font-semibold text-gray-900 mb-4">How This Works</h4>
        <div class="prose prose-sm max-w-none text-gray-700" v-html="requestTypeDetails.process_description"></div>
      </div>

      <div v-else-if="requestTypeDetails.description" class="bg-white border border-gray-200 rounded-lg p-6">
        <h4 class="text-lg font-semibold text-gray-900 mb-4">About This Application</h4>
        <p class="text-gray-700">{{ requestTypeDetails.description }}</p>
      </div>

      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">Before You Continue</h5>
            <p class="text-yellow-800 text-sm mt-1">
              Please review this information carefully. Make sure you understand the process, fees, and timeframes before proceeding with your application.
            </p>
          </div>
        </div>
      </div>

      <div class="flex justify-center pt-4">
        <button
          type="button"
          @click="emit('continue')"
          class="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          I Understand - Continue to Application
        </button>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-500">No request type selected. Please go back and select a request type.</p>
    </div>

    <!-- Council Meeting Modal (Simple Version) -->
    <div
      v-if="showPreAppMeetingModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closePreAppMeetingModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-hidden">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">Request Council Meeting</h3>
          <button
            @click="closePreAppMeetingModal"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="overflow-y-auto max-h-[calc(90vh-140px)] px-6 py-4">
          <div class="space-y-4">
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p class="text-sm text-blue-900">
                A council meeting allows you to discuss your proposal with council planners before formally submitting your application.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Meeting Format *</label>
              <select
                v-model="currentPreAppMeeting.meeting_format"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="In Person">In Person</option>
                <option value="Video Call">Video Call</option>
                <option value="Phone Call">Phone Call</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Meeting Purpose *</label>
              <textarea
                v-model="currentPreAppMeeting.meeting_purpose"
                rows="4"
                placeholder="Describe what you'd like to discuss in this meeting..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Preferred Date & Time</label>
              <input
                v-model="currentPreAppMeeting.preferred_time_slot_1_start"
                type="datetime-local"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">Select your preferred date and time. The council will confirm or propose an alternative.</p>
            </div>
          </div>
        </div>

        <div class="sticky bottom-0 bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t border-gray-200">
          <button
            @click="closePreAppMeetingModal"
            type="button"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="savePreAppMeeting"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            :disabled="!currentPreAppMeeting.meeting_purpose"
          >
            Request Meeting
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  requestTypeDetails: {
    type: Object,
    default: null
  },
  councilName: {
    type: String,
    default: ''
  },
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['continue', 'update:modelValue'])

// Pre-app meeting state
const preAppMeetingNotRequired = ref(props.modelValue?.pre_app_meeting_not_required || false)
const preAppMeetings = ref(props.modelValue?.pre_app_meetings || [])
const showPreAppMeetingModal = ref(false)
const currentPreAppMeeting = ref({
  meeting_type: 'Council Meeting',
  meeting_format: 'In Person',
  meeting_purpose: '',
  preferred_time_slot_1_start: null
})

// Watch for changes in pre-app meeting data and emit to parent
watch([preAppMeetingNotRequired, preAppMeetings], () => {
  emit('update:modelValue', {
    ...props.modelValue,
    pre_app_meeting_not_required: preAppMeetingNotRequired.value,
    pre_app_meetings: preAppMeetings.value
  })
}, { deep: true })

const openPreAppMeetingModal = () => {
  currentPreAppMeeting.value = {
    meeting_type: 'Council Meeting',
    meeting_format: 'In Person',
    meeting_purpose: '',
    preferred_time_slot_1_start: null
  }
  showPreAppMeetingModal.value = true
}

const closePreAppMeetingModal = () => {
  showPreAppMeetingModal.value = false
}

const savePreAppMeeting = () => {
  preAppMeetings.value.push({ ...currentPreAppMeeting.value })
  closePreAppMeetingModal()
}

const removePreAppMeeting = (index) => {
  if (confirm('Remove this council meeting request?')) {
    preAppMeetings.value.splice(index, 1)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('en-NZ', {
    dateStyle: 'medium',
    timeStyle: 'short'
  })
}
</script>
