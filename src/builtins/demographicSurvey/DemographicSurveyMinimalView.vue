<script setup>
import { reactive, computed } from 'vue'
// Import and initialize Smile API
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { Input } from '@/uikit/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/uikit/components/ui/select'
import { cn } from '@/uikit/lib/utils'
import { TitleTwoCol, ConstrainedPage } from '@/uikit/layouts'
/**
 * Initialize the Smile API for view management
 */
const api = useViewAPI()
/**
 * Configure the survey steps for the demographic survey
 */
api.steps.append([{ id: 'survey_page1' }])
/**
 * Computed property to check if the age is valid (18-120)
 */
const isAgeValid = computed(() => {
  const age = api.persist.forminfo.age
  if (!age || age === '') return false
  const ageNum = Number(age)
  return !isNaN(ageNum) && ageNum >= 18 && ageNum <= 120
})
/**
 * Initialize form data in local storage if not already defined
 * Persists demographic survey responses across page navigation
 */
if (!api.persist.isDefined('forminfo')) {
  api.persist.forminfo = reactive({
    age: '',
    gender: '',
    gender_self_describe: '',
    race: '',
    hispanic: '',
    fluent_english: '',
    normal_vision: '',
    color_blind: '',
    learning_disability: '',
    neurodevelopmental_disorder: '',
    psychiatric_disorder: '',
    country: '',
    zipcode: '',
    education_level: '',
    household_income: '',
  })
}
/**
 * Computed property to check if gender self-describe field should be shown
 */
const showGenderSelfDescribe = computed(() => {
  return api.persist.forminfo.gender === 'self_describe'
})
/**
 * Computed property to check if page one is complete
 * Validates that all required fields on the first page are filled and participant is at least 18
 */
const page_one_complete = computed(() => {
  const ageValid = isAgeValid.value
  const genderValid = api.persist.forminfo.gender !== ''
  const selfDescribeValid = showGenderSelfDescribe.value 
    ? api.persist.forminfo.gender_self_describe.trim() !== ''
    : true
  
  return ageValid && genderValid && selfDescribeValid
})
/**
 * Computed property to check if page two is complete
 * Validates that all required fields on the second page are filled
 */
const page_two_complete = computed(
  () =>
    api.persist.forminfo.color_blind !== '' &&
    api.persist.forminfo.learning_disability !== '' &&
    api.persist.forminfo.neurodevelopmental_disorder !== '' &&
    api.persist.forminfo.psychiatric_disorder !== ''
)
/**
 * Computed property to check if page three is complete
 * Validates that all required fields on the third page are filled
 */
const page_three_complete = computed(
  () =>
    api.persist.forminfo.country !== '' &&
    api.persist.forminfo.education_level !== '' &&
    api.persist.forminfo.household_income !== ''
)
/**
 * Autofill function for development and testing purposes
 * Pre-populates the form with sample data
 */
function autofill() {
  api.persist.forminfo.age = '25'
  api.persist.forminfo.gender = 'Woman'
  api.persist.forminfo.country = 'United States'
}
/**
 * Register the autofill function with the API for development mode
 */
api.setAutofill(autofill)
/**
 * Finish function to record form data and proceed to next view
 * Saves the demographic survey responses and navigates to the next step
 */
function finish() {
  api.recordForm('demographicForm', api.persist.forminfo)
  api.goNextView()
}
</script>
<template>
  <!-- Main container with responsive layout -->
  <ConstrainedPage
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <!-- Two-column layout with title and form content -->
    <TitleTwoCol leftFirst leftWidth="w-1/3" :responsiveUI="api.config.responsiveUI">
      <!-- Page title and description section -->
      <template #title>
        <h3 class="text-3xl font-bold mb-4"><i-fa6-solid-person class="inline mr-2" />Demographic Information</h3>
        <p class="text-lg mb-8">
          Please complete this short demographics survey. 
          Your privacy will be maintained and the data will not be linked to your online identity (e.g.,
          email, participant ID).
        </p>
      </template>
      <!-- Left sidebar with page-specific instructions -->
      <template #left>
        <div v-if="api.pathString === 'survey_page1'" class="text-left text-muted-foreground">
          <h3 class="text-lg font-bold mb-2">Basic Info</h3>
          <p class="text-md font-light text-muted-foreground">
            Please report your age and gender.
          </p>
        </div>
      </template>
      <!-- Right content area with form sections -->
      <template #right>
        <!-- Page 1: Basic demographic information -->
        <div v-if="api.pathString === 'survey_page1'" class="border border-border text-left bg-muted p-6 rounded-lg">
          <!-- Age field -->
          <div class="mb-3">
            <label class="block text-md font-semibold text-foreground mb-2"> Age </label>
            <Input
              v-model="api.persist.forminfo.age"
              type="number"
              placeholder="Enter your age"
              min="18"
              max="120"
              :class="[
                'w-full bg-background text-base',
                api.persist.forminfo.age && !isAgeValid ? 'border-red-500' : '',
                isAgeValid ? 'border-green-500' : ''
              ]"
            />
            <p class="text-xs text-muted-foreground mt-1">
              Enter your age in years (required) - must be 18 or older
            </p>
            <p v-if="api.persist.forminfo.age && !isAgeValid" class="text-xs text-red-500 mt-1">
              Age must be at least 18 years old
            </p>
          </div>
          <!-- Gender field -->
          <div class="mb-3">
            <label class="block text-md font-semibold text-foreground mb-2"> Gender </label>
            <Select v-model="api.persist.forminfo.gender">
              <SelectTrigger class="w-full bg-background dark:bg-background text-base">
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Man">Man</SelectItem>
                <SelectItem value="Woman">Woman</SelectItem>
                <SelectItem value="Non-binary">Non-binary</SelectItem>
                <SelectItem value="self_describe">Prefer to self-describe</SelectItem>
              </SelectContent>
            </Select>
            <p class="text-xs text-muted-foreground mt-1">Which option best describes your gender identity? (required)</p>
            
            <!-- Self-describe text input (shown when "Prefer to self-describe" is selected) -->
            <div v-if="showGenderSelfDescribe" class="mt-3">
              <Input
                v-model="api.persist.forminfo.gender_self_describe"
                placeholder="Please describe your gender identity"
                class="w-full bg-background text-base"
              />
              <p class="text-xs text-muted-foreground mt-1">Please provide your gender identity (required)</p>
            </div>
          </div>
          <!-- Navigation section -->
          <hr class="border-border my-6" />
          <div class="flex justify-end">
            <Button variant="outline" :disabled="!page_one_complete" @click="finish()">
              Continue
              <i-fa6-solid-arrow-right />
            </Button>
          </div>
        </div>
      </template>
    </TitleTwoCol>
  </ConstrainedPage>
</template>