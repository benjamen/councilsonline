# UX/UI Review: RMA Consent-Type-Specific Implementation

**Reviewer Role:** UX/UI Expert
**Review Date:** 2025-11-30
**Implementation:** RMA Consent-Type-Specific Conditional Logic
**Overall Grade:** A- (Excellent with minor improvements recommended)

---

## Executive Summary

The implementation demonstrates **strong UX principles** with intelligent progressive disclosure, clear visual hierarchy, and helpful contextual guidance. The interface successfully balances regulatory compliance with user-friendliness. However, there are **7 critical UX improvements** that would elevate this from good to exceptional.

### Strengths ✅
- ✅ Excellent progressive disclosure (fields appear only when relevant)
- ✅ Clear visual feedback (colored borders, state changes)
- ✅ Contextual help text with RMA statutory references
- ✅ Appropriate use of color psychology (amber for warnings, green for positive)
- ✅ Consistent component patterns across steps

### Areas for Improvement ⚠️
- ⚠️ **Critical**: No real-time validation feedback on duration inputs
- ⚠️ **High**: Missing accessibility features (ARIA labels, keyboard navigation)
- ⚠️ **High**: Lapsing period lacks guidance on when to choose which option
- ⚠️ **Medium**: Financial Contribution section adds cognitive load unnecessarily
- ⚠️ **Medium**: No visual indication of which fields are consent-type dependent
- ⚠️ **Low**: Text could be more scannable with better typography
- ⚠️ **Low**: Mobile responsiveness not optimized for complex multi-field inputs

---

## Detailed Component Reviews

### 1. Step 7B - Consent Details Component

#### 1.1 Duration Fields (Per Consent Type)

**Current State:**
```vue
<div class="flex gap-4 items-center">
  <div class="flex-1">
    <input
      v-model.number="getDurationData(ct.consent_type).duration_years"
      type="number"
      :min="1"
      :max="getMaxDuration(ct.consent_type)"
      placeholder="e.g., 10"
      :disabled="getDurationData(ct.consent_type).duration_unlimited"
      class="w-full px-3 py-2 border border-gray-300 rounded-lg"
    />
  </div>
  <span class="text-gray-600">years</span>
  <label v-if="canBeUnlimited(ct.consent_type)">
    <input v-model="getDurationData(ct.consent_type).duration_unlimited" type="checkbox" />
    <span class="text-sm">Unlimited</span>
  </label>
</div>
```

**UX Issues:**

🔴 **CRITICAL: No Real-Time Validation Feedback**
- User enters 50 years for Water Permit (max 35)
- No immediate visual feedback until form submission
- Error message appears far from input (if at all)

**Recommended Fix:**
```vue
<div class="flex gap-4 items-center">
  <div class="flex-1">
    <input
      v-model.number="getDurationData(ct.consent_type).duration_years"
      type="number"
      :min="1"
      :max="getMaxDuration(ct.consent_type)"
      placeholder="e.g., 10"
      :disabled="getDurationData(ct.consent_type).duration_unlimited"
      :class="[
        'w-full px-3 py-2 border rounded-lg',
        'focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
        // Validation states
        getDurationValidationClass(ct.consent_type)
      ]"
      @blur="validateDuration(ct.consent_type)"
    />
    <!-- Real-time validation message -->
    <p v-if="getDurationError(ct.consent_type)"
       class="mt-1 text-xs text-red-600 flex items-center gap-1">
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/>
      </svg>
      {{ getDurationError(ct.consent_type) }}
    </p>
    <!-- Validation success -->
    <p v-else-if="durationTouched[ct.consent_type] && getDurationData(ct.consent_type).duration_years"
       class="mt-1 text-xs text-green-600 flex items-center gap-1">
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/>
      </svg>
      Valid duration
    </p>
  </div>
  <span class="text-gray-600">years</span>
  <label v-if="canBeUnlimited(ct.consent_type)" class="flex items-center gap-2 whitespace-nowrap">
    <input type="checkbox" v-model="getDurationData(ct.consent_type).duration_unlimited" />
    <span class="text-sm">Unlimited</span>
  </label>
</div>
```

**Additional JavaScript needed:**
```javascript
const durationTouched = ref({})
const durationErrors = ref({})

const validateDuration = (consentType) => {
  durationTouched.value[consentType] = true
  const data = getDurationData(consentType)

  if (data.duration_unlimited) {
    durationErrors.value[consentType] = null
    return
  }

  const max = getMaxDuration(consentType)
  const years = data.duration_years

  if (!years || years < 1) {
    durationErrors.value[consentType] = 'Duration must be at least 1 year'
  } else if (years > max) {
    durationErrors.value[consentType] = `${consentType} cannot exceed ${max} years (s.123 RMA)`
  } else {
    durationErrors.value[consentType] = null
  }
}

const getDurationValidationClass = (consentType) => {
  if (!durationTouched.value[consentType]) return 'border-gray-300'
  if (durationErrors.value[consentType]) return 'border-red-300 bg-red-50'
  if (getDurationData(consentType).duration_years) return 'border-green-300 bg-green-50'
  return 'border-gray-300'
}

const getDurationError = (consentType) => durationErrors.value[consentType]
```

**Impact:** HIGH - Prevents user frustration and reduces form submission errors

---

#### 1.2 Lapsing Period Field

**Current State:**
```vue
<label class="block text-sm font-medium text-gray-700 mb-2">
  Lapsing Period
</label>
<select v-model.number="localData.lapsing_period_years">
  <option :value="5">5 years (standard)</option>
  <option :value="10">10 years (renewable energy)</option>
  <option v-if="isCoastalPermit" :value="3">3 years (aquaculture)</option>
</select>
<p class="mt-1 text-xs text-gray-500">
  Time period before consent lapses if not given effect to (s.125 RMA)
</p>
```

**UX Issues:**

🟡 **HIGH: Lacks Decision-Making Guidance**
- Users see options but don't know which to choose
- "Renewable energy" and "aquaculture" labels aren't self-explanatory
- No indication when 10-year option is appropriate

**Recommended Fix:**
```vue
<div>
  <label class="block text-sm font-medium text-gray-700 mb-2">
    Lapsing Period
    <button type="button" @click="showLapsingHelp = !showLapsingHelp"
            class="ml-2 text-blue-600 hover:text-blue-700">
      <svg class="w-4 h-4 inline" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"/>
      </svg>
    </button>
  </label>

  <!-- Expandable help panel -->
  <div v-if="showLapsingHelp" class="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
    <p class="font-medium text-blue-900 mb-2">How to choose lapsing period:</p>
    <ul class="space-y-1 text-blue-800">
      <li><strong>5 years:</strong> Standard for most consents - construction/use must begin within 5 years</li>
      <li><strong>10 years:</strong> For renewable energy projects requiring longer development timelines (s.125(1A) RMA)</li>
      <li v-if="isCoastalPermit"><strong>3 years:</strong> For aquaculture activities in coastal marine area</li>
    </ul>
  </div>

  <select v-model.number="localData.lapsing_period_years"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
    <option :value="5">5 years - Standard lapsing period</option>
    <option :value="10">10 years - Renewable energy projects</option>
    <option v-if="isCoastalPermit" :value="3">3 years - Aquaculture activities</option>
  </select>

  <p class="mt-1 text-xs text-gray-500">
    Time period before consent lapses if not given effect to (s.125 RMA)
  </p>
</div>
```

**Impact:** MEDIUM - Improves user confidence in decision-making

---

#### 1.3 Financial Contribution Section

**Current State:**
```vue
<div class="border-t border-gray-200 pt-6">
  <h3 class="text-lg font-semibold text-gray-900 mb-4">Financial Contribution (s.108(2)(a) RMA)</h3>
  <p class="text-sm text-gray-600 mb-4">
    Council may impose financial contributions as a condition of consent
  </p>
  <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <div class="flex items-start">
      <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0">...</svg>
      <div>
        <h5 class="font-semibold text-blue-900 text-sm">Information Only</h5>
        <p class="text-blue-800 text-sm mt-1">
          Financial contributions are determined by council policy and will be advised during
          processing if applicable. No action required at this stage.
        </p>
      </div>
    </div>
  </div>
</div>
```

**UX Issues:**

🟡 **MEDIUM: Unnecessary Cognitive Load**
- Takes up significant screen space
- Requires user to read and understand "no action needed"
- Section heading with divider suggests importance, but content says "ignore this"
- Interrupts flow between actionable sections

**Recommended Fix - Option A (Minimize):**
```vue
<details class="border-t border-gray-200 pt-4">
  <summary class="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900 flex items-center gap-2">
    <svg class="w-4 h-4 transform transition-transform" :class="{'rotate-90': open}"
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
    </svg>
    About Financial Contributions (s.108 RMA)
  </summary>
  <div class="mt-3 pl-6 text-sm text-gray-600">
    Council may impose financial contributions as a condition of consent. These are determined
    by council policy and will be advised during processing if applicable. No action required
    at this stage.
  </div>
</details>
```

**Recommended Fix - Option B (Move to help):**
Remove from main form flow, add to contextual help sidebar or tooltip system.

**Impact:** MEDIUM - Reduces cognitive load, improves form completion time

---

#### 1.4 Fast-Track Processing Section

**Current State:**
```vue
<div v-if="eligibleForFastTrack" class="space-y-3">
  <div class="bg-green-50 border border-green-200 rounded-lg p-4">
    <div class="flex items-start">
      <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3">...</svg>
      <div>
        <h5 class="font-semibold text-green-900 text-sm">Eligible for Fast-Track</h5>
        <p class="text-green-800 text-sm mt-1">
          Based on your consent type and activity status (Controlled), this application is
          eligible for fast-track processing.
        </p>
      </div>
    </div>
  </div>

  <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer">
    <input v-model="localData.request_fast_track" type="checkbox" />
    <div class="ml-3">
      <span class="font-medium text-gray-900">Request fast-track processing</span>
      <p class="text-xs text-gray-600 mt-1">
        I would like this application to be processed under fast-track provisions
        (subject to council availability)
      </p>
    </div>
  </label>
</div>
```

**UX Strengths:** ✅
- ✅ Excellent use of color psychology (green = positive opportunity)
- ✅ Clear eligibility messaging
- ✅ Progressive disclosure (only shows when eligible)
- ✅ Appropriate caveats ("subject to council availability")

**Minor Enhancement:**
```vue
<div v-if="eligibleForFastTrack" class="space-y-3">
  <div class="bg-green-50 border border-green-200 rounded-lg p-4">
    <div class="flex items-start">
      <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0">...</svg>
      <div class="flex-1">
        <h5 class="font-semibold text-green-900 text-sm">Eligible for Fast-Track Processing</h5>
        <p class="text-green-800 text-sm mt-1">
          Your application qualifies for expedited processing (s.87AAB RMA) with reduced timeframes.
        </p>
        <!-- NEW: Benefit callout -->
        <div class="mt-2 flex items-center gap-2 text-green-700 text-xs font-medium">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Typically processed within 10 working days (vs. 20 working days standard)
        </div>
      </div>
    </div>
  </div>
  <!-- ... checkbox label unchanged ... -->
</div>
```

**Impact:** LOW - Adds value clarity, no critical issues present

---

### 2. Step 10 (formerly 11) - NES & Hazards Component

#### 2.1 Natural Hazards Warning (LUC/SC)

**Current State:**
```vue
<div v-if="requiresHazardsAssessment" class="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0">...</svg>
    <div>
      <h5 class="font-semibold text-amber-900 text-sm">Critical Assessment Required - s.106 RMA</h5>
      <p class="text-amber-800 text-sm mt-1">
        <strong>Important:</strong> Under s.106 RMA, councils <strong>must refuse</strong>
        Land Use and Subdivision consents if building on land subject to certain natural
        hazards would:
      </p>
      <ul class="text-amber-800 text-sm mt-2 ml-4 list-disc">
        <li>Accelerate, worsen, or result in material damage</li>
        <li>Create or worsen a natural hazard on the property or other property</li>
      </ul>
      <p class="text-amber-800 text-sm mt-2">
        Please carefully identify all natural hazards affecting the site and detail mitigation measures.
      </p>
    </div>
  </div>
</div>
```

**UX Strengths:** ✅
- ✅ Perfect use of amber/warning color
- ✅ Strong visual hierarchy
- ✅ Clear consequence messaging ("must refuse")
- ✅ Actionable instruction at end

**Minor Enhancement - Improve Scannability:**
```vue
<div v-if="requiresHazardsAssessment" class="mb-4 p-4 bg-amber-50 border-l-4 border-amber-400 rounded-r-lg">
  <div class="flex items-start">
    <svg class="w-6 h-6 text-amber-600 mr-3 flex-shrink-0">...</svg>
    <div>
      <h5 class="font-bold text-amber-900 text-base mb-2">
        ⚠️ Critical Assessment Required - s.106 RMA
      </h5>
      <div class="bg-white bg-opacity-50 rounded p-3 mb-3">
        <p class="text-amber-900 text-sm font-medium">
          Under s.106 RMA, councils <strong class="text-red-700">must refuse</strong>
          Land Use and Subdivision consents if building on land subject to natural hazards would:
        </p>
      </div>
      <ul class="text-amber-800 text-sm space-y-1 ml-4 list-none">
        <li class="flex items-start gap-2">
          <span class="text-amber-600 font-bold">•</span>
          <span>Accelerate, worsen, or result in material damage to property</span>
        </li>
        <li class="flex items-start gap-2">
          <span class="text-amber-600 font-bold">•</span>
          <span>Create or worsen a natural hazard on this or other properties</span>
        </li>
      </ul>
      <div class="mt-3 pt-3 border-t border-amber-300">
        <p class="text-amber-900 text-sm font-medium">
          → Please identify all natural hazards affecting the site and detail mitigation measures below.
        </p>
      </div>
    </div>
  </div>
</div>
```

**Impact:** LOW - Already excellent, enhancements improve scannability

---

#### 2.2 "No Hazards" Confirmation

**Current State:**
```vue
<div v-if="requiresHazardsAssessment && (!localData.natural_hazards || localData.natural_hazards.length === 0)">
  <label class="flex items-start p-3 border-2 rounded-lg cursor-pointer bg-white">
    <input v-model="localData.no_natural_hazards_confirmed" type="checkbox" />
    <div class="ml-3">
      <span class="font-medium text-gray-900">I confirm there are no natural hazards affecting this site</span>
      <p class="text-xs text-gray-600 mt-1">
        By checking this box, I confirm that I have considered all potential natural hazards
        (flooding, erosion, landslip, earthquake, tsunami, etc.) and none are applicable to this site.
      </p>
    </div>
  </label>
</div>
```

**UX Strengths:** ✅
- ✅ Good "moment of friction" UX pattern
- ✅ Lists example hazard types
- ✅ Clear declaration language

**Enhancement - Add Consequence Clarity:**
```vue
<div v-if="requiresHazardsAssessment && (!localData.natural_hazards || localData.natural_hazards.length === 0)"
     class="mb-4">
  <label class="flex items-start p-4 border-2 rounded-lg cursor-pointer bg-white transition-all"
         :class="localData.no_natural_hazards_confirmed ? 'border-blue-600 bg-blue-50' : 'border-amber-300 hover:border-amber-400 bg-amber-50'">
    <input v-model="localData.no_natural_hazards_confirmed" type="checkbox"
           class="mt-1 h-5 w-5 text-blue-600" />
    <div class="ml-3">
      <span class="font-semibold text-gray-900 text-base">
        ✓ I confirm there are no natural hazards affecting this site
      </span>
      <p class="text-sm text-gray-700 mt-2 leading-relaxed">
        By checking this box, I confirm that I have considered <strong>all potential natural hazards</strong>
        including:
      </p>
      <div class="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-600">
        <div class="flex items-center gap-1">
          <span class="text-blue-600">→</span> Flooding
        </div>
        <div class="flex items-center gap-1">
          <span class="text-blue-600">→</span> Landslip
        </div>
        <div class="flex items-center gap-1">
          <span class="text-blue-600">→</span> Erosion
        </div>
        <div class="flex items-center gap-1">
          <span class="text-blue-600">→</span> Earthquake
        </div>
        <div class="flex items-center gap-1">
          <span class="text-blue-600">→</span> Tsunami
        </div>
        <div class="flex items-center gap-1">
          <span class="text-blue-600">→</span> Subsidence
        </div>
      </div>
      <p class="text-xs text-gray-600 mt-3 italic">
        ...and confirm that <strong>none</strong> are applicable to this site.
      </p>
      <!-- NEW: Consequence warning -->
      <div class="mt-3 p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
        <strong>Note:</strong> False declarations may result in consent refusal under s.106 RMA.
      </div>
    </div>
  </label>
</div>
```

**Impact:** MEDIUM - Strengthens the "moment of friction," ensures informed confirmation

---

## Accessibility (WCAG 2.1 AA) Audit

### Critical Issues Found 🔴

#### 1. Missing ARIA Labels
**Issue:** Duration inputs lack descriptive labels for screen readers
```vue
<!-- BEFORE -->
<input v-model.number="getDurationData(ct.consent_type).duration_years" type="number" />

<!-- AFTER -->
<input
  v-model.number="getDurationData(ct.consent_type).duration_years"
  type="number"
  :id="`duration-${ct.consent_type.toLowerCase().replace(' ', '-')}`"
  :aria-label="`Duration in years for ${ct.consent_type} consent`"
  :aria-describedby="`duration-help-${ct.consent_type.toLowerCase().replace(' ', '-')}`"
  :aria-invalid="!!getDurationError(ct.consent_type)"
/>
<p :id="`duration-help-${ct.consent_type.toLowerCase().replace(' ', '-')}`" class="mt-1 text-xs text-gray-500">
  {{ getDurationHelpText(ct.consent_type) }}
</p>
```

#### 2. Keyboard Navigation Issues
**Issue:** Checkbox cards not keyboard accessible
```vue
<!-- BEFORE -->
<div @click="toggleNES(nes.value)" class="...cursor-pointer">
  <input type="checkbox" :checked="..." readonly class="pointer-events-none" />
</div>

<!-- AFTER -->
<div
  role="checkbox"
  :aria-checked="getNESData(nes.value).applies"
  :tabindex="0"
  @click="toggleNES(nes.value)"
  @keydown.space.prevent="toggleNES(nes.value)"
  @keydown.enter.prevent="toggleNES(nes.value)"
  class="...cursor-pointer focus:ring-2 focus:ring-blue-500 focus:outline-none"
>
  <input type="checkbox" :checked="..." readonly class="pointer-events-none" aria-hidden="true" />
</div>
```

#### 3. Color-Only Information
**Issue:** Validation states use color alone (fails WCAG 1.4.1)
```vue
<!-- BEFORE -->
<input :class="isValid ? 'border-green-300' : 'border-red-300'" />

<!-- AFTER -->
<div class="relative">
  <input :class="isValid ? 'border-green-300' : 'border-red-300'"
         :aria-invalid="!isValid" />
  <!-- Icon indicator -->
  <span class="absolute right-2 top-2.5" aria-hidden="true">
    <svg v-if="isValid" class="w-5 h-5 text-green-600">✓</svg>
    <svg v-else class="w-5 h-5 text-red-600">✗</svg>
  </span>
</div>
```

#### 4. Focus Indicators
**Issue:** Custom checkboxes override browser focus styles
```css
/* Add to component styles */
<style scoped>
.cursor-pointer:focus-within {
  @apply ring-2 ring-blue-500 ring-offset-2;
}

input[type="checkbox"]:focus {
  @apply ring-2 ring-blue-500 ring-offset-1;
}

input[type="number"]:focus {
  @apply ring-2 ring-blue-500 border-blue-500;
}
</style>
```

---

## Mobile Responsiveness Issues

### Issue: Complex Multi-Field Duration Inputs
**Problem:** On mobile, duration input + "years" + checkbox don't fit well

**Current Layout (Desktop):**
```
[________Input________] years  [ ] Unlimited
```

**Mobile Breaks:**
```
[___Input___] y  [ ]
              Unl...
```

**Recommended Fix:**
```vue
<div class="flex flex-col sm:flex-row gap-3 sm:gap-4 sm:items-center">
  <div class="flex-1">
    <div class="flex items-center gap-2">
      <input class="flex-1 min-w-0" ... />
      <span class="text-gray-600 whitespace-nowrap">years</span>
    </div>
  </div>
  <label v-if="canBeUnlimited(ct.consent_type)"
         class="flex items-center gap-2 pl-4 sm:pl-0 border-l-2 sm:border-l-0 border-gray-200">
    <input type="checkbox" ... />
    <span class="text-sm whitespace-nowrap">Unlimited</span>
  </label>
</div>
```

---

## Information Architecture Improvements

### Recommendation: Visual Consent Type Dependency Indicators

**Problem:** Users can't quickly scan to see which fields apply to their selected consent types

**Solution:** Add subtle visual indicators

```vue
<!-- Duration Section -->
<div class="space-y-4">
  <div v-for="ct in props.modelValue.consent_types" :key="ct.consent_type"
       class="relative border border-gray-200 rounded-lg p-4 bg-gray-50">
    <!-- Consent type badge -->
    <div class="absolute -top-2 left-3 px-2 py-0.5 bg-blue-600 text-white text-xs font-medium rounded">
      {{ ct.consent_type }}
    </div>
    <!-- ... rest of content ... -->
  </div>
</div>

<!-- Conditional Sections -->
<div v-if="isSubdivision" class="border-t border-gray-200 pt-6 relative">
  <!-- Consent type indicator ribbon -->
  <div class="absolute -top-3 right-4 flex items-center gap-2 px-3 py-1 bg-purple-100 border border-purple-300 rounded-full text-xs font-medium text-purple-800">
    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
      <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"/>
    </svg>
    Subdivision only
  </div>
  <h3>Consent Notice (s.221 RMA)</h3>
  <!-- ... -->
</div>
```

---

## Typography & Readability Improvements

### Issue: Dense Text Blocks

**Problem:** Long paragraphs in help text reduce scannability

**Example - Lapsing Period Help:**
```vue
<!-- BEFORE -->
<p class="mt-1 text-xs text-gray-500">
  Time period before consent lapses if not given effect to (s.125 RMA)
</p>

<!-- AFTER - More scannable -->
<div class="mt-1 text-xs text-gray-600 space-y-0.5">
  <p class="font-medium text-gray-700">Lapsing period:</p>
  <p>Timeframe to commence work after consent granted</p>
  <p class="text-gray-500 italic">(s.125 RMA)</p>
</div>
```

---

## Performance & Loading States

### Missing: Loading States for Dynamic Content

**Issue:** When consent types change, duration fields appear instantly - jarring on slow connections

**Recommended Addition:**
```vue
<transition-group name="fade-slide" tag="div" class="space-y-4">
  <div v-for="ct in props.modelValue.consent_types"
       :key="ct.consent_type"
       class="...">
    <!-- Content -->
  </div>
</transition-group>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
```

---

## Summary of Recommendations

### Priority Matrix

| Priority | Issue | Component | Effort | Impact |
|----------|-------|-----------|--------|--------|
| 🔴 P0 | Real-time duration validation | Step7B | Medium | High |
| 🔴 P0 | ARIA labels for inputs | Both | Low | High |
| 🔴 P0 | Keyboard navigation | Both | Medium | High |
| 🟡 P1 | Lapsing period guidance | Step7B | Low | Medium |
| 🟡 P1 | Mobile responsive duration inputs | Step7B | Medium | Medium |
| 🟡 P1 | Color-only validation states | Both | Low | Medium |
| 🟢 P2 | Financial contribution minimization | Step7B | Low | Low |
| 🟢 P2 | Visual consent type indicators | Both | Medium | Low |
| 🟢 P2 | Typography improvements | Both | Low | Low |
| 🟢 P2 | Loading state transitions | Both | Low | Low |

### Estimated Implementation Time
- **P0 (Critical):** 8-12 hours
- **P1 (High):** 6-8 hours
- **P2 (Nice-to-have):** 4-6 hours
- **Total:** 18-26 hours for full implementation

---

## Overall Assessment

### Strengths
The implementation demonstrates strong UX fundamentals:
- Smart progressive disclosure
- Excellent color psychology usage
- Clear visual hierarchy
- Helpful contextual guidance
- Good use of "moments of friction" for critical decisions

### Weaknesses
- Accessibility gaps (WCAG 2.1 AA compliance)
- Missing real-time validation feedback
- Some guidance gaps in decision-making
- Mobile optimization needed

### Grade: A- (Excellent with Room for Improvement)

**Recommendation:** Address P0 and P1 items before production release. P2 items can be incremental improvements.

---

**Review Completed By:** UX/UI Expert Analysis
**Next Steps:** Implement recommendations in priority order, conduct user testing with target audience (consent applicants)
