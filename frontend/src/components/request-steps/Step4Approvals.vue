<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Boundary Approvals & Affected Parties</h2>
    <p class="text-gray-600 mb-8">Obtain approvals for boundary activities and identify affected parties (RMA s.95A-s.95F)</p>

    <div class="space-y-8">
      <!-- Permitted Boundary Activity (PBA) Section -->
      <PBASection v-model="localData" />

      <!-- Affected Parties Section -->
      <AffectedPartiesSection v-model="localData" />

      <!-- Guidance -->
      <InfoBox title="Affected Parties Guidance" variant="warning">
        <ul class="space-y-1 list-disc list-inside">
          <li>Consider immediate neighbors, landowners with shared boundaries</li>
          <li>Infrastructure providers (e.g., power, water, telecommunications)</li>
          <li>Parties with interests over the land (e.g., easements, covenants)</li>
          <li>Anyone who may experience adverse effects from your proposal</li>
          <li>Written approvals under s.95E can reduce notification requirements and costs</li>
        </ul>
      </InfoBox>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import PBASection from "../approvals/PBASection.vue"
import AffectedPartiesSection from "../approvals/AffectedPartiesSection.vue"
import InfoBox from "../shared/InfoBox.vue"

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(["update:modelValue"])

const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value)
})
</script>
