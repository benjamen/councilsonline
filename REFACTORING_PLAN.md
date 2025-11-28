# NewRequest.vue Refactoring Plan

## Current State
- **Total lines:** 5,730
- **Template:** ~3,600 lines
- **Script:** ~2,100 lines
- **Bundle size:** 143.59 kB (31.09 kB gzipped)

## Problems
1. **Monolithic component** - difficult to maintain and test
2. **Large bundle** - all code loads upfront even for unused steps
3. **Context switching** - developers must scroll through thousands of lines
4. **Reusability** - logic tied to single component

## Refactoring Strategy

### Phase 1: Extract Step 5 RC Details Component (Priority 1)
**Size:** 1,538 lines → Target: 3-5 smaller components

#### 1.1 Create `RCDetailsStep.vue`
Extract entire Step 5 section with sub-components:

**Sub-components to create:**
- `RCConsentTypes.vue` - Consent type selection (~100 lines)
- `RCActivityStatus.vue` - Activity status dropdown (~80 lines)
- `RCAEESection.vue` - AEE structured fields + upload (~240 lines)
- `RCInvoicing.vue` - Invoice details section (~90 lines)
- `RCDeclarations.vue` - Statutory declarations (~55 lines)
- `RCNaturalHazards.vue` - Hazards assessment (~200 lines)
- `RCNESAssessments.vue` - NES assessments (~250 lines)
- `RCHAILActivities.vue` - HAIL activities section (~150 lines)
- `RCAffectedParties.vue` - Affected parties management (~120 lines)
- `RCConditions.vue` - Proposed conditions (~200 lines)

**Props interface:**
```typescript
interface RCDetailsProps {
  modelValue: FormData
  onUpdate: (data: Partial<FormData>) => void
  validationErrors?: Record<string, string>
}
```

#### 1.2 Create Composables for Shared Logic
Extract reusable logic into `src/composables/`:

**File upload composable:**
```typescript
// useFileUpload.ts
export function useFileUpload(options: {
  maxSize: number
  allowedTypes: string[]
  fieldName: string
}) {
  const handleUpload = (event: Event) => { ... }
  const removeFile = () => { ... }
  return { handleUpload, removeFile, file, error }
}
```

**Validation composable:**
```typescript
// useFormValidation.ts
export function useFormValidation(formData: Ref<FormData>) {
  const validateStep = (step: number) => { ... }
  const errors = ref<Record<string, string>>({})
  return { validateStep, errors, isValid }
}
```

**Array management composable:**
```typescript
// useArrayField.ts
export function useArrayField<T>(
  initialValue: T,
  fieldName: string
) {
  const items = ref<T[]>([])
  const add = () => { ... }
  const remove = (index: number) => { ... }
  const edit = (index: number) => { ... }
  return { items, add, remove, edit }
}
```

### Phase 2: Extract Step 4 Property Details (Priority 2)
**Size:** 374 lines → Target: 2-3 components

#### Components:
- `PropertyDetailsStep.vue` - Main wrapper
- `PropertySearch.vue` - Property selection/search (~80 lines)
- `OwnerDetails.vue` - Owner information section (~90 lines)
- `PropertyInfo.vue` - Property address and details (~120 lines)

### Phase 3: Implement Code Splitting (Priority 3)

#### Dynamic imports for steps:
```typescript
// NewRequest.vue
const RCDetailsStep = defineAsyncComponent({
  loader: () => import('./components/steps/RCDetailsStep.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200
})

const PropertyDetailsStep = defineAsyncComponent({
  loader: () => import('./components/steps/PropertyDetailsStep.vue'),
  loadingComponent: LoadingSpinner
})
```

**Benefits:**
- Only load step components when needed
- Reduce initial bundle by ~40%
- Faster initial page load

### Phase 4: Create Shared UI Components (Priority 4)

Extract reusable UI patterns:
- `FormSection.vue` - Consistent section styling
- `FileUploadField.vue` - Reusable file upload with validation
- `ConditionalFields.vue` - Show/hide field groups
- `ArrayFieldManager.vue` - Generic add/remove/edit list

### Phase 5: State Management Optimization (Priority 5)

Consider Pinia store for complex state:
```typescript
// stores/requestForm.ts
export const useRequestFormStore = defineStore('requestForm', {
  state: () => ({
    formData: { ... },
    currentStep: 1,
    validationErrors: {}
  }),
  actions: {
    updateField(field: string, value: any) { ... },
    validateCurrentStep() { ... },
    submitRequest() { ... }
  }
})
```

## Implementation Order

### Week 1: Foundation
1. ✅ Create composables directory structure
2. ✅ Extract file upload logic to `useFileUpload.ts`
3. ✅ Extract validation logic to `useFormValidation.ts`
4. ✅ Create array field helper `useArrayField.ts`

### Week 2: Step 5 Refactoring
1. Create `components/steps/rc-details/` directory
2. Extract AEE section to `RCAEESection.vue` (test individually)
3. Extract Invoicing to `RCInvoicing.vue`
4. Extract Declarations to `RCDeclarations.vue`
5. Extract remaining sections
6. Create main `RCDetailsStep.vue` wrapper
7. Test integrated Step 5

### Week 3: Step 4 & Code Splitting
1. Extract Property Details components
2. Implement dynamic imports for both steps
3. Test lazy loading behavior
4. Measure bundle size improvements

### Week 4: Polish & Optimization
1. Create shared UI components
2. Add loading states
3. Add error boundaries
4. Performance testing
5. Documentation updates

## Expected Results

### Bundle Size Reduction
**Current:**
- NewRequest.vue: 143.59 kB (31.09 kB gzipped)

**Target:**
- NewRequest.vue (core): ~40 kB (10 kB gzipped)
- RCDetailsStep.vue: ~60 kB (15 kB gzipped) - lazy loaded
- PropertyDetailsStep.vue: ~20 kB (5 kB gzipped) - lazy loaded
- Shared composables: ~10 kB (3 kB gzipped)

**Initial load reduction:** ~60% (from 143 kB to ~60 kB)

### Maintainability Improvements
- Average component size: ~150 lines (down from 5,730)
- Single Responsibility: Each component has one clear purpose
- Testability: Components can be unit tested in isolation
- Reusability: Composables can be used in other forms

### Developer Experience
- Faster file navigation
- Easier to review PRs
- Clearer component boundaries
- Better TypeScript support

## Migration Path

### Step 1: Create parallel structure (no breaking changes)
- New components alongside existing code
- Feature flag for new components
- A/B testing in development

### Step 2: Gradual migration
- Enable new Step 5 component
- Monitor for issues
- Roll back if needed

### Step 3: Complete migration
- Remove old code
- Update documentation
- Celebrate! 🎉

## Risk Mitigation

1. **Backwards compatibility:** Keep old code until thoroughly tested
2. **Feature flags:** Ability to toggle between old/new components
3. **Comprehensive testing:** Unit tests + E2E tests for all new components
4. **Performance monitoring:** Track bundle sizes and load times
5. **User feedback:** Beta testing with select users

## Success Metrics

- ✅ Bundle size reduced by >50%
- ✅ Average component size <200 lines
- ✅ Zero regression in functionality
- ✅ Improved Lighthouse performance score
- ✅ Positive developer feedback

## Next Steps

1. Review and approve this plan
2. Create feature branch: `refactor/split-newrequest-component`
3. Start with composables (low risk, high value)
4. Incrementally refactor Step 5 sections
5. Test thoroughly before merging

---

**Status:** Ready for implementation
**Estimated effort:** 3-4 weeks (part-time)
**Risk level:** Medium (mitigated by gradual approach)
**Value:** High (long-term maintainability + performance)
