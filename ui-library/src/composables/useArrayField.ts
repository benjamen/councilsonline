/**
 * Composable for managing array-based form fields
 * Useful for sections like Affected Parties, HAIL Activities, Specialist Reports, etc.
 *
 * @example
 * ```typescript
 * const { items, add, remove, edit, isEditing, editingIndex } = useArrayField({
 *   initialValue: () => ({
 *     name: '',
 *     email: '',
 *     address: ''
 *   }),
 *   onAdd: (item) => console.log('Added:', item),
 *   onRemove: (index) => console.log('Removed:', index)
 * })
 * ```
 */

import { ref, computed, type Ref } from 'vue'

export interface ArrayFieldOptions<T> {
  /**
   * Factory function to create a new empty item
   * @returns A new item with default values
   */
  initialValue: () => T

  /**
   * Initial items (optional)
   */
  items?: T[]

  /**
   * Callback when item is added
   */
  onAdd?: (item: T) => void

  /**
   * Callback when item is removed
   */
  onRemove?: (index: number, item: T) => void

  /**
   * Callback when item is updated
   */
  onUpdate?: (index: number, item: T) => void

  /**
   * Validation function for items
   */
  validate?: (item: T) => string | null
}

export interface ArrayFieldReturn<T> {
  /** Array of items */
  items: Ref<T[]>

  /** Add a new item to the array */
  add: () => void

  /** Remove an item by index */
  remove: (index: number) => void

  /** Start editing an item */
  edit: (index: number) => void

  /** Save the currently edited item */
  save: (item: T) => void

  /** Cancel editing */
  cancelEdit: () => void

  /** Whether currently editing an item */
  isEditing: Ref<boolean>

  /** Index of item being edited (-1 if not editing) */
  editingIndex: Ref<number>

  /** Current item being edited */
  editingItem: Ref<T | null>

  /** Clear all items */
  clear: () => void

  /** Validation error for current editing item */
  validationError: Ref<string | null>

  /** Total number of items */
  count: Ref<number>

  /** Whether array is empty */
  isEmpty: Ref<boolean>
}

export function useArrayField<T>(
  options: ArrayFieldOptions<T>
): ArrayFieldReturn<T> {
  const items = ref<T[]>(options.items || []) as Ref<T[]>
  const editingIndex = ref<number>(-1)
  const editingItem = ref<T | null>(null) as Ref<T | null>
  const validationError = ref<string | null>(null)

  const isEditing = computed(() => editingIndex.value !== -1)
  const count = computed(() => items.value.length)
  const isEmpty = computed(() => items.value.length === 0)

  const add = () => {
    const newItem = options.initialValue()
    items.value.push(newItem)
    options.onAdd?.(newItem)
  }

  const remove = (index: number) => {
    if (index < 0 || index >= items.value.length) {
      console.error('Invalid index:', index)
      return
    }

    const removedItem = items.value[index]
    items.value.splice(index, 1)
    options.onRemove?.(index, removedItem)

    // If currently editing this item, cancel edit
    if (editingIndex.value === index) {
      cancelEdit()
    }
  }

  const edit = (index: number) => {
    if (index < 0 || index >= items.value.length) {
      console.error('Invalid index:', index)
      return
    }

    editingIndex.value = index
    // Create a copy to avoid mutating original during edit
    editingItem.value = JSON.parse(JSON.stringify(items.value[index]))
    validationError.value = null
  }

  const save = (item: T) => {
    if (editingIndex.value === -1) {
      console.error('No item is being edited')
      return
    }

    // Validate if validator provided
    if (options.validate) {
      const error = options.validate(item)
      if (error) {
        validationError.value = error
        return
      }
    }

    // Save the edited item
    items.value[editingIndex.value] = item
    options.onUpdate?.(editingIndex.value, item)

    // Clear editing state
    editingIndex.value = -1
    editingItem.value = null
    validationError.value = null
  }

  const cancelEdit = () => {
    editingIndex.value = -1
    editingItem.value = null
    validationError.value = null
  }

  const clear = () => {
    items.value = []
    cancelEdit()
  }

  return {
    items,
    add,
    remove,
    edit,
    save,
    cancelEdit,
    isEditing,
    editingIndex,
    editingItem,
    validationError,
    count,
    isEmpty,
    clear
  }
}

/**
 * Extended version with modal/dialog support
 */
export interface ArrayFieldWithModalOptions<T> extends ArrayFieldOptions<T> {
  /**
   * Modal title when adding new item
   */
  addModalTitle?: string

  /**
   * Modal title when editing item
   */
  editModalTitle?: string
}

export interface ArrayFieldWithModalReturn<T> extends ArrayFieldReturn<T> {
  /** Whether modal is open */
  showModal: Ref<boolean>

  /** Open modal for adding new item */
  openAddModal: () => void

  /** Open modal for editing item */
  openEditModal: (index: number) => void

  /** Close modal */
  closeModal: () => void

  /** Current modal title */
  modalTitle: Ref<string>
}

export function useArrayFieldWithModal<T>(
  options: ArrayFieldWithModalOptions<T>
): ArrayFieldWithModalReturn<T> {
  const baseField = useArrayField(options)
  const showModal = ref(false)
  const modalTitle = ref('')

  const openAddModal = () => {
    baseField.editingItem.value = options.initialValue()
    baseField.editingIndex.value = -1
    modalTitle.value = options.addModalTitle || 'Add Item'
    showModal.value = true
  }

  const openEditModal = (index: number) => {
    baseField.edit(index)
    modalTitle.value = options.editModalTitle || 'Edit Item'
    showModal.value = true
  }

  const closeModal = () => {
    showModal.value = false
    baseField.cancelEdit()
  }

  return {
    ...baseField,
    showModal,
    openAddModal,
    openEditModal,
    closeModal,
    modalTitle
  }
}
