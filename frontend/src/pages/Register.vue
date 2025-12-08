<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-2xl">
      <!-- Logo & Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4 shadow-lg">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Create Your Account</h1>
        <p class="text-gray-600">Join thousands using Lodgeick for council requests</p>
      </div>

      <!-- Requester vs Agent Selection -->
      <div class="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 text-center">Choose Account Type</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="p-6 border-2 border-blue-600 bg-blue-50 rounded-lg">
            <div class="text-center">
              <svg class="w-12 h-12 mx-auto mb-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Register as Requester</h3>
              <p class="text-sm text-gray-600 mb-4">Submit requests for yourself or on behalf of an organization</p>
              <div class="text-sm text-blue-900 font-medium">✓ Currently selected</div>
            </div>
          </div>
          <button
            type="button"
            @click="$router.push({ name: 'CompanyRegistration' })"
            class="p-6 border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 rounded-lg transition text-left"
          >
            <div class="text-center">
              <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Register as Agent</h3>
              <p class="text-sm text-gray-600 mb-4">Consultants or representatives submitting on behalf of clients</p>
              <div class="text-sm text-blue-600 font-medium">Click to register as agent →</div>
            </div>
          </button>
        </div>
      </div>

      <!-- Registration Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <form @submit.prevent="submit" class="space-y-6">
          <!-- Account Type Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">
              Account Type <span class="text-red-500">*</span>
            </label>
            <p class="text-xs text-gray-500 mb-3">Select the entity type you're registering as</p>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                @click="applicantType = 'Individual'"
                :class="[
                  'p-4 border-2 rounded-lg text-center transition',
                  applicantType === 'Individual'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <svg class="w-8 h-8 mx-auto mb-2" :class="applicantType === 'Individual' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <div class="text-sm font-medium" :class="applicantType === 'Individual' ? 'text-blue-900' : 'text-gray-700'">
                  Individual
                </div>
                <div class="text-xs text-gray-500 mt-1">Person/Civilian</div>
              </button>
              <button
                type="button"
                @click="applicantType = 'Company'"
                :class="[
                  'p-4 border-2 rounded-lg text-center transition',
                  applicantType === 'Company'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <svg class="w-8 h-8 mx-auto mb-2" :class="applicantType === 'Company' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <div class="text-sm font-medium" :class="applicantType === 'Company' ? 'text-blue-900' : 'text-gray-700'">
                  Company
                </div>
                <div class="text-xs text-gray-500 mt-1">NZ Registered</div>
              </button>
              <button
                type="button"
                @click="applicantType = 'Trust'"
                :class="[
                  'p-4 border-2 rounded-lg text-center transition',
                  applicantType === 'Trust'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <svg class="w-8 h-8 mx-auto mb-2" :class="applicantType === 'Trust' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <div class="text-sm font-medium" :class="applicantType === 'Trust' ? 'text-blue-900' : 'text-gray-700'">
                  Trust
                </div>
                <div class="text-xs text-gray-500 mt-1">Trust Entity</div>
              </button>
              <button
                type="button"
                @click="applicantType = 'Organisation'"
                :class="[
                  'p-4 border-2 rounded-lg text-center transition',
                  applicantType === 'Organisation'
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <svg class="w-8 h-8 mx-auto mb-2" :class="applicantType === 'Organisation' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <div class="text-sm font-medium" :class="applicantType === 'Organisation' ? 'text-blue-900' : 'text-gray-700'">
                  Organisation
                </div>
                <div class="text-xs text-gray-500 mt-1">Charity/NPO</div>
              </button>
            </div>
          </div>

          <!-- Council Selection (Optional) -->
          <div>
            <CouncilSelector
              v-model="selectedCouncil"
              label="Default Council (Optional)"
              description="Select your preferred council for submitting requests. You can change this later."
              display-mode="dropdown"
              :required="false"
              :show-clear-button="true"
            />
          </div>

          <!-- Personal Information -->
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
                First Name <span class="text-red-500">*</span>
              </label>
              <Input
                id="first_name"
                v-model="formData.first_name"
                type="text"
                required
                placeholder="John"
                class="w-full"
              />
            </div>
            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
                Last Name <span class="text-red-500">*</span>
              </label>
              <Input
                id="last_name"
                v-model="formData.last_name"
                type="text"
                required
                placeholder="Doe"
                class="w-full"
              />
            </div>
          </div>

          <!-- Contact Information -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email Address <span class="text-red-500">*</span>
            </label>
            <Input
              id="email"
              v-model="formData.email"
              type="email"
              required
              placeholder="you@example.com"
              class="w-full"
              @blur="validateEmailField"
            />
            <p v-if="emailError" class="mt-1 text-xs text-red-600">{{ emailError }}</p>
          </div>

          <div>
            <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
              Phone Number <span class="text-red-500">*</span>
            </label>
            <input
              id="phone"
              v-model="formData.phone"
              type="tel"
              required
              placeholder="021 234 5678 or 09 123 4567"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @blur="validatePhoneField"
            />
            <p v-if="phoneError" class="mt-1 text-xs text-red-600">{{ phoneError }}</p>
            <p v-else class="mt-1 text-xs text-gray-500">NZ mobile (02x) or landline (03-09)</p>
          </div>

          <!-- Properties Section -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-medium text-gray-900">Properties</h3>
                <p class="text-xs text-gray-500 mt-1">
                  {{ applicantType === 'Individual' ? 'Add your properties (at least one required)' : 'Add your properties (optional)' }}
                </p>
              </div>
              <button
                type="button"
                @click="openAddPropertyModal"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add Property
              </button>
            </div>

            <!-- Properties List -->
            <div v-if="properties.length > 0" class="space-y-2">
              <div
                v-for="(property, index) in properties"
                :key="index"
                class="border border-gray-200 rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <h4 class="text-sm font-semibold text-gray-900">{{ property.property_name }}</h4>
                      <span v-if="property.is_default" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        Default
                      </span>
                    </div>
                    <p class="text-sm text-gray-600 mt-1">{{ property.street }}</p>
                    <p class="text-xs text-gray-500">{{ property.suburb }}{{ property.suburb && property.city ? ', ' : '' }}{{ property.city }} {{ property.postcode }}</p>
                  </div>
                  <div class="flex items-center gap-2 ml-4">
                    <button
                      v-if="!property.is_default"
                      type="button"
                      @click="setDefaultProperty(index)"
                      class="text-xs text-blue-600 hover:text-blue-800"
                    >
                      Set as Default
                    </button>
                    <button
                      type="button"
                      @click="removeProperty(index)"
                      class="text-red-600 hover:text-red-800"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-6 border-2 border-dashed border-gray-300 rounded-lg">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <p class="mt-2 text-sm text-gray-500">No properties added yet</p>
            </div>
          </div>

          <!-- Add Property Modal -->
          <div v-if="showAddPropertyModal" class="fixed inset-0 z-50 overflow-y-auto">
            <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
              <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeAddPropertyModal"></div>

              <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <h3 class="text-lg font-medium text-gray-900 mb-4">Add Property</h3>

                  <div class="space-y-4">
                    <div>
                      <label for="property_name" class="block text-sm font-medium text-gray-700 mb-2">
                        Property Name <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="property_name"
                        v-model="currentProperty.property_name"
                        type="text"
                        required
                        placeholder="e.g., Home, Investment Property, Beach House"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <AddressLookup
                        v-model="selectedAddress"
                        id="property_address_modal"
                        label="Property Address"
                        placeholder="Start typing the property address..."
                        description="Search for the property address in New Zealand"
                        :required="true"
                        @address-selected="handleAddressSelected"
                      />
                    </div>

                    <div>
                      <label class="flex items-center">
                        <input
                          v-model="currentProperty.is_default"
                          type="checkbox"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span class="ml-2 text-sm text-gray-700">Set as default property</span>
                      </label>
                    </div>
                  </div>
                </div>

                <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-2">
                  <button
                    type="button"
                    @click="addProperty"
                    class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  >
                    Add Property
                  </button>
                  <button
                    type="button"
                    @click="closeAddPropertyModal"
                    class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Company/Organisation Details -->
          <div v-if="applicantType === 'Company' || applicantType === 'Organisation'" class="space-y-4">
            <div>
              <label for="organization_name" class="block text-sm font-medium text-gray-700 mb-2">
                {{ applicantType === 'Company' ? 'Company Name' : 'Organisation Name' }} <span class="text-red-500">*</span>
              </label>
              <Input
                id="organization_name"
                v-model="formData.organization_name"
                type="text"
                required
                :placeholder="applicantType === 'Company' ? 'ABC Construction Ltd' : 'Community Trust'"
                class="w-full"
              />
            </div>
            <div v-if="applicantType === 'Company'">
              <label for="company_number" class="block text-sm font-medium text-gray-700 mb-2">
                Company Number (Optional)
              </label>
              <Input
                id="company_number"
                v-model="formData.company_number"
                type="text"
                placeholder="1234567"
                class="w-full"
              />
            </div>
          </div>

          <!-- Trust Details -->
          <div v-if="applicantType === 'Trust'" class="space-y-4">
            <div>
              <label for="trust_name" class="block text-sm font-medium text-gray-700 mb-2">
                Trust Name <span class="text-red-500">*</span>
              </label>
              <Input
                id="trust_name"
                v-model="formData.trust_name"
                type="text"
                required
                placeholder="Smith Family Trust"
                class="w-full"
              />
            </div>
          </div>

          <!-- Password -->
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                Password <span class="text-red-500">*</span>
              </label>
              <Input
                id="password"
                v-model="formData.password"
                type="password"
                required
                placeholder="Min. 8 characters"
                class="w-full"
                @input="validatePasswordField"
              />
              <p v-if="passwordError" class="mt-1 text-xs text-red-600">{{ passwordError }}</p>
              <p v-else-if="passwordStrength" class="mt-1 text-xs" :class="passwordStrengthClass">
                Password strength: {{ passwordStrength }}
              </p>
            </div>
            <div>
              <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password <span class="text-red-500">*</span>
              </label>
              <Input
                id="confirm_password"
                v-model="formData.confirm_password"
                type="password"
                required
                placeholder="Repeat password"
                class="w-full"
                @blur="validatePasswordMatch"
              />
              <p v-if="confirmPasswordError" class="mt-1 text-xs text-red-600">{{ confirmPasswordError }}</p>
            </div>
          </div>

          <!-- Terms and Conditions -->
          <div class="flex items-start">
            <input
              id="terms"
              v-model="formData.terms"
              type="checkbox"
              required
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
            />
            <label for="terms" class="ml-2 block text-sm text-gray-700">
              I agree to the
              <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Terms of Service</a>
              and
              <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Privacy Policy</a>
            </label>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-700">{{ errorMessage }}</p>
            </div>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            :loading="isLoading"
            variant="solid"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-base font-medium"
          >
            <template v-if="!isLoading">
              Create Account
            </template>
            <template v-else>
              Creating account...
            </template>
          </Button>
        </form>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-4 bg-white text-gray-500">or</span>
          </div>
        </div>

        <!-- SSO Options -->
        <div class="space-y-3">
          <button
            type="button"
            class="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition"
          >
            <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign up with Google
          </button>
        </div>
      </div>

      <!-- Sign In Link -->
      <div class="text-center mt-6">
        <p class="text-sm text-gray-600">
          Already have an account?
          <router-link :to="{ name: 'Login' }" class="font-medium text-blue-600 hover:text-blue-700">
            Sign in
          </router-link>
        </p>
      </div>

      <!-- Back to Home -->
      <div class="text-center mt-4">
        <router-link to="/" class="text-sm text-gray-500 hover:text-gray-700 inline-flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { Input, Button } from "frappe-ui"
import CouncilSelector from "../components/CouncilSelector.vue"
import AddressLookup from "../components/AddressLookup.vue"
import { useCouncilStore } from "../stores/councilStore"
import { validateNZPhoneNumber, validateEmail, validatePassword } from "../utils/validation"

const router = useRouter()
const route = useRoute()
const councilStore = useCouncilStore()

const applicantType = ref('Individual')
const selectedCouncil = ref(null)
const selectedAddress = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

// Form data
const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  password: '',
  confirm_password: '',
  organization_name: '',
  company_number: '',
  trust_name: '',
  terms: false
})

// Validation errors
const phoneError = ref('')
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')
const passwordStrength = ref('')

const passwordStrengthClass = computed(() => {
  if (passwordStrength.value === 'strong') return 'text-green-600'
  if (passwordStrength.value === 'medium') return 'text-yellow-600'
  return 'text-red-600'
})

// Properties management
const properties = ref([])
const showAddPropertyModal = ref(false)
const currentProperty = ref({
  property_name: '',
  street: '',
  suburb: '',
  city: '',
  postcode: '',
  is_default: false
})

const openAddPropertyModal = () => {
  currentProperty.value = {
    property_name: '',
    street: '',
    suburb: '',
    city: '',
    postcode: '',
    is_default: properties.value.length === 0 // First property is default
  }
  selectedAddress.value = null
  showAddPropertyModal.value = true
}

const closeAddPropertyModal = () => {
  showAddPropertyModal.value = false
  currentProperty.value = {
    property_name: '',
    street: '',
    suburb: '',
    city: '',
    postcode: '',
    is_default: false
  }
  selectedAddress.value = null
}

const addProperty = () => {
  if (!currentProperty.value.property_name) {
    alert('Please enter a property name')
    return
  }

  if (!selectedAddress.value) {
    alert('Please select a property address')
    return
  }

  // If this property is set as default, remove default from others
  if (currentProperty.value.is_default) {
    properties.value.forEach(p => p.is_default = false)
  }

  properties.value.push({
    property_name: currentProperty.value.property_name,
    street: selectedAddress.value.street_address || selectedAddress.value.full_address,
    suburb: selectedAddress.value.suburb || '',
    city: selectedAddress.value.city || '',
    postcode: selectedAddress.value.postcode || '',
    is_default: currentProperty.value.is_default
  })

  closeAddPropertyModal()
}

const removeProperty = (index) => {
  if (confirm('Are you sure you want to remove this property?')) {
    const wasDefault = properties.value[index].is_default
    properties.value.splice(index, 1)

    // If we removed the default and have other properties, set the first one as default
    if (wasDefault && properties.value.length > 0) {
      properties.value[0].is_default = true
    }
  }
}

const setDefaultProperty = (index) => {
  properties.value.forEach((p, i) => {
    p.is_default = i === index
  })
}

onMounted(() => {
  // Check if council was preselected via URL
  if (councilStore.preselectedFromUrl) {
    selectedCouncil.value = councilStore.preselectedFromUrl
  }
})

// Validation functions
const validatePhoneField = () => {
  const validation = validateNZPhoneNumber(formData.value.phone)
  if (!validation.isValid) {
    phoneError.value = validation.message
  } else {
    phoneError.value = ''
    // Auto-format phone number
    formData.value.phone = validation.formatted
  }
  return validation.isValid
}

const validateEmailField = () => {
  const validation = validateEmail(formData.value.email)
  if (!validation.isValid) {
    emailError.value = validation.message
  } else {
    emailError.value = ''
  }
  return validation.isValid
}

const validatePasswordField = () => {
  const validation = validatePassword(formData.value.password)
  if (!validation.isValid) {
    passwordError.value = validation.message
    passwordStrength.value = ''
  } else {
    passwordError.value = ''
    passwordStrength.value = validation.strength
  }
  return validation.isValid
}

const validatePasswordMatch = () => {
  if (formData.value.password !== formData.value.confirm_password) {
    confirmPasswordError.value = 'Passwords do not match'
    return false
  }
  confirmPasswordError.value = ''
  return true
}

const handleAddressSelected = (address) => {
  selectedAddress.value = address
}

function submit() {
  // Clear previous errors
  errorMessage.value = ''
  phoneError.value = ''
  emailError.value = ''
  passwordError.value = ''
  confirmPasswordError.value = ''

  // Validate all fields
  const isPhoneValid = validatePhoneField()
  const isEmailValid = validateEmailField()
  const isPasswordValid = validatePasswordField()
  const isPasswordMatch = validatePasswordMatch()

  if (!isPhoneValid || !isEmailValid || !isPasswordValid || !isPasswordMatch) {
    errorMessage.value = 'Please correct the errors above before submitting'
    return
  }

  // Validate account-type specific fields
  if (applicantType.value === 'Individual' && properties.value.length === 0) {
    errorMessage.value = 'At least one property is required for individual requesters'
    return
  }

  if ((applicantType.value === 'Company' || applicantType.value === 'Organisation') && !formData.value.organization_name) {
    errorMessage.value = `${applicantType.value} name is required`
    return
  }

  if (applicantType.value === 'Trust' && !formData.value.trust_name) {
    errorMessage.value = 'Trust name is required'
    return
  }

  if (!formData.value.terms) {
    errorMessage.value = 'You must agree to the Terms of Service and Privacy Policy'
    return
  }

  isLoading.value = true

  // Prepare user data
  const userData = {
    email: formData.value.email,
    first_name: formData.value.first_name,
    last_name: formData.value.last_name,
    phone: formData.value.phone,
    password: formData.value.password,
    user_role: 'requester', // This is a requester registration
    applicant_type: applicantType.value, // Individual, Company, Trust, Organisation (entity type)
    properties: properties.value // Send all properties
  }

  // Add type-specific data
  if (applicantType.value === 'Company' || applicantType.value === 'Organisation') {
    userData.organization_name = formData.value.organization_name
    userData.company_number = formData.value.company_number
  } else if (applicantType.value === 'Trust') {
    userData.trust_name = formData.value.trust_name
  }

  // Add council_code if selected
  if (selectedCouncil.value) {
    userData.council_code = selectedCouncil.value
  }

  // Call registration API
  fetch('/api/method/lodgeick.api.register_user', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token
    },
    body: JSON.stringify(userData)
  })
  .then(response => response.json())
  .then(data => {
    isLoading.value = false

    if (data.message && data.message.success) {
      // Success - redirect to login with success message
      router.push({
        name: 'Login',
        query: { registered: 'true' }
      })
    } else if (data.exc || data._server_messages) {
      // Server error
      const serverMessages = data._server_messages ? JSON.parse(data._server_messages) : []
      const errorMsg = serverMessages.length > 0
        ? JSON.parse(serverMessages[0]).message
        : 'Registration failed. Please try again.'
      errorMessage.value = errorMsg
      console.error('Registration error:', data.exc || data._server_messages)
    } else {
      errorMessage.value = 'Registration failed. Please try again.'
    }
  })
  .catch(error => {
    isLoading.value = false
    errorMessage.value = 'Network error. Please check your connection and try again.'
    console.error('Registration error:', error)
  })
}
</script>
