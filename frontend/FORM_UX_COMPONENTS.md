# Enhanced Form UI/UX Components

This document describes the new form components designed to provide a better user experience with modern UI design, camera integration, and improved accessibility.

## Components Overview

### 1. FormSection.vue

A reusable wrapper component that provides consistent styling and structure for form sections.

**Features:**
- Icon slot for custom section icons
- Required indicator badge
- Optional subtitle
- Footer slot for additional content
- Hover effects and transitions

**Usage:**
```vue
<FormSection
  title="Personal Information"
  subtitle="Basic details about yourself"
  :required="true"
>
  <template #icon>
    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <!-- Your icon SVG -->
    </svg>
  </template>

  <!-- Your form fields here -->
  <input type="text" v-model="name" />

  <template #footer>
    <p class="text-sm text-gray-500">Additional information</p>
  </template>
</FormSection>
```

**Props:**
- `title` (String, required): Section title
- `subtitle` (String, optional): Descriptive subtitle
- `required` (Boolean, default: false): Shows required badge

---

### 2. CameraUpload.vue

Advanced file upload component with integrated camera capture functionality.

**Features:**
- Camera capture with live preview
- Grid overlay for better photo composition
- File browser fallback
- Image preview thumbnails
- Upload progress indicator
- Multiple file support
- File size validation (default: 20MB max)
- Drag & drop support (coming soon)
- Auto-upload on file selection

**Usage:**
```vue
<CameraUpload
  v-model="photos"
  label="Profile Photo"
  help-text="Take a photo or upload a recent picture"
  :required="true"
  :allow-camera="true"
  :multiple="false"
  accept="image/*"
  @upload="handlePhotoUpload"
/>
```

**Props:**
- `label` (String, required): Label text
- `helpText` (String): Helper text below upload buttons
- `modelValue` (Array, default: []): Array of uploaded files
- `accept` (String, default: 'image/*,.pdf'): Accepted file types
- `multiple` (Boolean, default: false): Allow multiple files
- `required` (Boolean, default: false): Mark as required field
- `allowCamera` (Boolean, default: true): Show camera button
- `maxSize` (Number, default: 20MB): Maximum file size in bytes

**Events:**
- `update:modelValue`: Emitted when files change
- `upload`: Emitted for each file (fileData, callback)

**File Object Structure:**
```javascript
{
  file: File,        // Original File object
  name: String,      // File name
  size: Number,      // File size in bytes
  type: String,      // MIME type
  preview: String,   // Base64 preview (for images)
  uploadDate: String // ISO date string
}
```

---

### 3. PersonalInfoForm.vue

Complete personal information form with all fields commonly needed for government applications.

**Features:**
- Photo upload section with camera
- Full name input
- Sex dropdown (Male/Female)
- Civil status dropdown
- Date of birth picker with age calculation
- Email and mobile number fields
- Complete address form (street, barangay, municipality, province, ZIP)
- Auto-populated location fields
- Field validation and help text
- Responsive grid layout

**Usage:**
```vue
<PersonalInfoForm
  v-model="personalInfo"
  :municipality="'Taytay'"
  :province="'Rizal'"
  :barangay-list="barangays"
  :photo-required="true"
/>
```

**Props:**
- `modelValue` (Object, required): Form data object
- `municipality` (String, default: 'Taytay'): Municipality name (read-only)
- `province` (String, default: 'Rizal'): Province name (read-only)
- `barangayList` (Array): List of barangays for dropdown
- `photoRequired` (Boolean, default: false): Make photo required

**Model Object Structure:**
```javascript
{
  full_name: String,
  sex: String,           // 'Male' | 'Female'
  civil_status: String,  // 'Single' | 'Married' | 'Widowed' | 'Separated' | 'Divorced'
  date_of_birth: String, // YYYY-MM-DD format
  email: String,
  mobile_number: String, // 11 digits
  street_address: String,
  barangay: String,
  municipality: String,
  province: String,
  zip_code: String,
  photos: Array          // CameraUpload files
}
```

---

### 4. DocumentsUploadForm.vue

Document upload management with support for multiple document types.

**Features:**
- Configurable document types
- Required/optional indicators
- Document examples list
- Upload progress tracking
- Document summary dashboard
- File preview for images
- Upload status indicators
- Missing document alerts

**Usage:**
```vue
<DocumentsUploadForm
  v-model="documents"
  :document-types="documentTypes"
/>
```

**Props:**
- `modelValue` (Object, required): Documents object keyed by document type
- `documentTypes` (Array): Array of document type configurations

**Document Type Configuration:**
```javascript
{
  key: String,          // Unique key (used in modelValue)
  label: String,        // Display name
  description: String,  // Help text
  examples: Array,      // List of examples
  required: Boolean,    // Is required?
  multiple: Boolean,    // Allow multiple files?
  accept: String        // File types (e.g., 'image/*,.pdf')
}
```

**Model Object Structure:**
```javascript
{
  valid_id: [           // Key matches documentType.key
    { file, name, size, type, preview, uploadDate }
  ],
  barangay_certificate: [...],
  // ... other document types
}
```

---

## Complete Example

See `ExampleFormUX.vue` for a complete multi-step form implementation:

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <!-- Step 1: Personal Info -->
    <PersonalInfoForm v-model="formData.personalInfo" />

    <!-- Step 2: Documents -->
    <DocumentsUploadForm v-model="formData.documents" :document-types="docTypes" />

    <!-- Navigation -->
    <button type="submit">Submit</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import PersonalInfoForm from '@/components/PersonalInfoForm.vue'
import DocumentsUploadForm from '@/components/DocumentsUploadForm.vue'

const formData = ref({
  personalInfo: {},
  documents: {}
})

const docTypes = [
  {
    key: 'valid_id',
    label: 'Valid ID',
    description: 'Government-issued ID',
    required: true,
    multiple: false
  }
]
</script>
```

---

## Camera Permissions

The camera feature requires browser permissions. Handle permission requests gracefully:

```javascript
// Check if camera is available
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  // Camera API available
} else {
  // Fallback to file upload only
}
```

**Browser Support:**
- Chrome 53+
- Firefox 36+
- Safari 11+
- Edge 12+

**Mobile Considerations:**
- On iOS, camera only works in Safari (not in-app browsers)
- Android works in Chrome and most browsers
- Always provide file upload fallback

---

## Styling & Theming

All components use Tailwind CSS classes. Customize by modifying:

```css
/* Primary color */
.bg-blue-600 → .bg-your-color-600
.text-blue-600 → .text-your-color-600
.border-blue-600 → .border-your-color-600

/* Rounded corners */
.rounded-lg → .rounded-xl (more rounded)
.rounded-lg → .rounded-md (less rounded)
```

---

## Accessibility

All components follow WCAG 2.1 AA guidelines:

- ✅ Keyboard navigation support
- ✅ Screen reader labels
- ✅ Focus indicators
- ✅ Color contrast ratios
- ✅ Error messaging
- ✅ Required field indicators

---

## File Upload Integration

The components emit upload events but don't handle actual file uploads. Implement upload handling:

```vue
<CameraUpload
  v-model="files"
  @upload="handleUpload"
/>

<script setup>
const handleUpload = async (fileData, callback) => {
  try {
    // Upload to server
    const formData = new FormData()
    formData.append('file', fileData.file)
    formData.append('doctype', 'Request Attachment')
    formData.append('docname', requestId)

    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    // Call callback to complete upload
    callback()
  } catch (error) {
    console.error('Upload failed:', error)
    alert('Upload failed. Please try again.')
  }
}
</script>
```

---

## Performance Optimization

**Large File Handling:**
- Files are processed asynchronously
- Previews generated only for images
- Upload progress tracked per file

**Memory Management:**
- Base64 previews limited to images only
- Large files don't generate previews
- File objects released after upload

**Mobile Optimization:**
- Camera resolution limited to 1920x1080
- JPEG compression at 90% quality
- Lazy loading for document lists

---

## Browser Console Testing

Test camera upload:
```javascript
// Check camera availability
navigator.mediaDevices.enumerateDevices()
  .then(devices => console.log(devices.filter(d => d.kind === 'videoinput')))

// Test file upload
const input = document.querySelector('input[type="file"]')
input.addEventListener('change', e => console.log('Selected:', e.target.files))
```

---

## Known Issues & Limitations

1. **iOS In-App Browsers**: Camera doesn't work in Facebook/Instagram in-app browsers. Solution: Show message to open in Safari.

2. **File Size Limits**: Server may have different limits than client. Always validate server-side.

3. **Image Orientation**: Some phones capture rotated images. Consider using EXIF orientation correction.

4. **Offline Support**: Camera requires navigator.mediaDevices which needs HTTPS or localhost.

---

## Future Enhancements

- [ ] Drag & drop file upload
- [ ] Image cropping/editing
- [ ] Multiple camera selection (front/back)
- [ ] QR code scanning
- [ ] Document OCR for auto-fill
- [ ] Cloud storage integration
- [ ] Offline file queuing

---

## Support

For issues or questions about these components:
1. Check the ExampleFormUX.vue demo
2. Review this documentation
3. Check browser console for errors
4. Test camera permissions in browser settings
