<script setup>
import { reactive, computed } from 'vue'

// Import and initialize Smile API
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/uikit/components/ui/select'
import { TitleTwoCol, ConstrainedPage } from '@/uikit/layouts'

/**
 * Initialize the Smile API for view management
 */
const api = useViewAPI()

/**
 * Initialize form data in local storage if not already defined
 * Persists demographic survey responses across page navigation
 */
if (!api.persist.isDefined('forminfo')) {
  api.persist.forminfo = reactive({
    country: 'United States',
    birth_year: '',
    fluent_english: '',
    normal_vision: '',
  })
}

/**
 * Generate a list of years for the birth year selector
 * From current year down to 100 years ago
 */
const currentYear = new Date().getFullYear()
const years = Array.from({ length: 110 }, (_, i) => (currentYear - i).toString())

/**
 * Computed property to check if the form is complete
 * Validates that all required fields are filled
 */
const is_complete = computed(() => {
  return (
    api.persist.forminfo.country === 'United States' &&
    api.persist.forminfo.birth_year !== '' &&
    api.persist.forminfo.fluent_english !== '' &&
    api.persist.forminfo.normal_vision !== ''
  )
})

/**
 * Autofill function for development and testing purposes
 * Pre-populates the form with sample data
 */
function autofill() {
  api.persist.forminfo.country = 'United States'
  api.persist.forminfo.birth_year = '1990'
  api.persist.forminfo.fluent_english = 'Yes'
  api.persist.forminfo.normal_vision = 'Yes'
}

/**
 * Register the autofill function with the API for development mode
 */
api.setAutofill(autofill)

/**
 * Finish function to record form data and proceed to next view
 */
function finish() {
  api.recordPageData(api.persist.forminfo)
  api.goNextView()
}
</script>

<template>
  <ConstrainedPage
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <TitleTwoCol leftFirst leftWidth="w-1/3" :responsiveUI="api.config.responsiveUI">
      <template #title>
        <h3 class="text-3xl font-bold mb-4"><i-fa6-solid-person class="inline mr-2" />Demographic Information</h3>
        <p class="text-lg mb-8">
          We request some information about you which we can use to understand aggregate differences between
          individuals. Your privacy will be maintained and the data will not be linked to your online identity.
        </p>
      </template>

      <template #left>
        <div class="text-left text-muted-foreground">
          <h3 class="text-lg font-bold mb-2">Background</h3>
          <p class="text-md font-light text-muted-foreground">
            Please provide information about your location, language background, and vision.
          </p>
        </div>
      </template>

      <template #right>
        <div class="border border-border text-left bg-muted p-6 rounded-lg">
          <!-- Country field -->
          <div class="mb-4">
            <label class="block text-md font-semibold text-foreground mb-2"> In which country are you based? </label>
            <Select v-model="api.persist.forminfo.country">
              <SelectTrigger class="w-full bg-background text-base">
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="United States">United States</SelectItem>
              </SelectContent>
            </Select>
            <p
              v-if="api.persist.forminfo.country && api.persist.forminfo.country !== 'United States'"
              class="text-sm text-destructive mt-2 font-medium"
            >
              You can only participate in this study if you are based in the United States.
            </p>
          </div>

          <!-- Birth Year field -->
          <div class="mb-4">
            <label class="block text-md font-semibold text-foreground mb-2"> What year were you born? </label>
            <Select v-model="api.persist.forminfo.birth_year">
              <SelectTrigger class="w-full bg-background text-base">
                <div class="flex items-center">
                  <i-lucide-calendar class="mr-2 h-4 w-4 opacity-50" />
                  <SelectValue placeholder="Select year" />
                </div>
              </SelectTrigger>
              <SelectContent class="max-h-[200px]">
                <SelectItem v-for="year in years" :key="year" :value="year">
                  {{ year }}
                </SelectItem>
              </SelectContent>
            </Select>
            <p class="text-xs text-muted-foreground mt-1">Select your birth year (required)</p>
          </div>

          <!-- English fluency field -->
          <div class="mb-4">
            <label class="block text-md font-semibold text-foreground mb-2"> Are you fluent in English? </label>
            <Select v-model="api.persist.forminfo.fluent_english">
              <SelectTrigger class="w-full bg-background text-base">
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Yes">Yes</SelectItem>
                <SelectItem value="No">No</SelectItem>
                <SelectItem value="I prefer not to say">I prefer not to say</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Vision field -->
          <div class="mb-4">
            <label class="block text-md font-semibold text-foreground mb-2">
              Do you have normal vision (glasses/contact lenses are fine)?
            </label>
            <Select v-model="api.persist.forminfo.normal_vision">
              <SelectTrigger class="w-full bg-background text-base">
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Yes">Yes</SelectItem>
                <SelectItem value="No">No</SelectItem>
                <SelectItem value="Unsure">Unsure</SelectItem>
                <SelectItem value="I prefer not to say">I prefer not to say</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Navigation section -->
          <hr class="border-border my-6" />
          <div class="flex justify-end">
            <Button variant="default" :disabled="!is_complete" @click="finish()"> Continue </Button>
          </div>
        </div>
      </template>
    </TitleTwoCol>
  </ConstrainedPage>
</template>
