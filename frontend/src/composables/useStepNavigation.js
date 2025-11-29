import { computed } from 'vue'

/**
 * Composable for step navigation logic
 * @param {Object} currentStep - The current step ref
 * @param {Object} steps - The computed steps array
 * @param {Function} canProceed - Function to check if can proceed from current step
 * @returns {Object} Navigation functions and computed properties
 */
export function useStepNavigation(currentStep, steps, canProceed) {
  /**
   * Total number of steps
   */
  const totalSteps = computed(() => steps.value.length)

  /**
   * Check if on first step
   */
  const isFirstStep = computed(() => currentStep.value === 1)

  /**
   * Check if on last step
   */
  const isLastStep = computed(() => currentStep.value === steps.value.length)

  /**
   * Get CSS class for step indicator
   */
  const getStepClass = (stepNumber) => {
    if (stepNumber < currentStep.value) {
      return 'bg-green-600 text-white' // Completed
    } else if (stepNumber === currentStep.value) {
      return 'bg-blue-600 text-white' // Current
    } else {
      return 'bg-gray-200 text-gray-600' // Upcoming
    }
  }

  /**
   * Navigate to next step
   */
  const nextStep = () => {
    if (canProceed()) {
      if (currentStep.value < steps.value.length) {
        currentStep.value++
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    } else {
      alert('Please complete all required fields before proceeding.')
    }
  }

  /**
   * Navigate to previous step
   */
  const previousStep = () => {
    if (currentStep.value > 1) {
      currentStep.value--
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  /**
   * Go back (navigate to previous step or home)
   */
  const goBack = () => {
    if (currentStep.value > 1) {
      previousStep()
    } else {
      // Navigate to home or previous page
      window.history.back()
    }
  }

  return {
    totalSteps,
    isFirstStep,
    isLastStep,
    getStepClass,
    nextStep,
    previousStep,
    goBack
  }
}
