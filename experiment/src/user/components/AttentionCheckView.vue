<script setup>
import { computed, reactive } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { Input } from '@/uikit/components/ui/input'
import { Label } from '@/uikit/components/ui/label'
import { Badge } from '@/uikit/components/ui/badge'
import { MultiSelect } from '@/uikit/components/ui/multiselect'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/uikit/components/ui/select'
import { Switch } from '@/uikit/components/ui/switch'
import { ConstrainedTaskWindow } from '@/uikit/layouts'

const api = useViewAPI()

/**
 * Registry of available attention check questions.
 * Questions can be referenced by their key in the props.questions array.
 */
const QUESTIONS = {
  easy_modality: {
    id: 'easy_modality',
    question: 'What symbols were presented during the working memory task?',
    answers: ['Numbers', 'Letters', 'Emoji'],
    correctAnswer: ['Letters'],
    help: 'Select all that apply. Skip this question if you do not remember the symbol type.',
    multiSelect: true,
  },
  easy_input_method: {
    id: 'easy_input_method',
    question: 'How were the answers selected during the working memory task?',
    answers: ['Keyboard', 'Mouse'],
    correctAnswer: ['Keyboard'],
    help: 'Skip this question if you do not remember the input method.',
    multiSelect: false,
  },
  easy_external_aid: {
    id: 'easy_external_aid',
    question: 'Did you use an external aid during the working memory task? For example, did you write down the list items to make it easier to remember them?',
    answers: ['Yes', 'No'],
    correctAnswer: ['No'],
    help: 'Skip this question if you prefer not to answer.',
    multiSelect: false,
  },
  hard_voro: {
    id: 'hard_voro',
    question: 'Vasta sõnaga avvo. Ainuq tuu sana, ei midägi muud.',
    placeholder: '',
    help: 'This question is in a different language. Only answer it if you understand the language.',
  },
  hard_maori: {
    id: 'hard_maori',
    question:
      'Tēnā koa, whakautu mai mā te kupu "maramatanga" i raro iho nei. Ko te kupu kotahi anake tō whakautu, ā, kaua e tāpiri atu i tētahi atu mea.',
    placeholder: '',
    help: 'This question is in a different language. Only answer it if you understand the language.',
  },
  hard_decimal: {
    id: 'hard_decimal',
    question:
      'Please enter the hexadecimal number you used to proceed during the instructions as a decimal number below.',
    placeholder: 'Enter decimal number...',
    help: 'Skip this question if you do not remember the number.',
    pattern: '^\\d+$',
    errorMessage: 'Please enter numbers only.',
  },
}

const props = defineProps({
  questions: {
    type: Array,
    required: true,
  },
})

// Map the keys or objects to full question definitions
const questionsList = props.questions.map((q) => (typeof q === 'string' ? QUESTIONS[q] : q))

// Set up steps for each question
api.steps.append(questionsList)

// Initialize persistence for responses to survive page reloads
if (!api.persist.isDefined('attentionResponses')) {
  const initialResponses = {}
  questionsList.forEach((q) => {
    initialResponses[q.id] = {
      userInput: q.multiSelect ? [] : '',
      isSkipped: false,
    }
  })
  api.persist.attentionResponses = reactive(initialResponses)
}

// Access current question from stepData
const currentQuestion = computed(() => api.stepData)

/**
 * Autofill function for development/testing - automatically fills correct answers
 * or skips if no correct answer is defined.
 */
function autofill() {
  questionsList.forEach((q) => {
    const response = api.persist.attentionResponses[q.id]
    if (q.correctAnswer) {
      response.userInput = q.multiSelect ? [...q.correctAnswer] : q.correctAnswer[0]
      response.isSkipped = false
    } else {
      response.isSkipped = true
    }
  })
  // Go to last question
  while (!api.isLastStep()) {
    api.goNextStep()
  }
}

api.setAutofill(autofill)

/**
 * Validation logic for a single question
 */
function isQuestionValid(q) {
  const response = api.persist.attentionResponses[q.id]
  if (response.isSkipped) return true

  // Selection question
  if (q.answers) {
    if (q.multiSelect) {
      return Array.isArray(response.userInput) && response.userInput.length > 0
    }
    return !!response.userInput
  }

  // Text input question
  const input = (response.userInput || '').trim()
  if (q.pattern) {
    const regex = new RegExp(q.pattern)
    return regex.test(input)
  }
  return input !== ''
}

/**
 * Check if a question has invalid input (user typed something but it doesn't match pattern)
 */
function hasInvalidInput(q) {
  const response = api.persist.attentionResponses[q.id]
  if (response.isSkipped || q.answers) return false

  const input = (response.userInput || '').trim()
  if (input === '') return false
  if (q.pattern) {
    const regex = new RegExp(q.pattern)
    return !regex.test(input)
  }
  return false
}

/**
 * Check if current question is valid
 */
const isCurrentValid = computed(() => {
  return isQuestionValid(currentQuestion.value)
})

/**
 * Check if all questions are either answered correctly or skipped
 */
const isAllValid = computed(() => {
  return questionsList.every((q) => isQuestionValid(q))
})

/**
 * Record data and proceed to the next view
 * Each question is recorded as a separate "trial" for flat data structure
 */
function finish() {
  if (!isAllValid.value) return

  questionsList.forEach((q) => {
    const response = api.persist.attentionResponses[q.id]
    let userInput = response.userInput

    // Normalize all responses to arrays for consistency
    let normalizedResponse
    if (typeof userInput === 'string') {
      normalizedResponse = [userInput.trim()]
    } else if (Array.isArray(userInput)) {
      normalizedResponse = userInput
    } else {
      normalizedResponse = []
    }

    // Record each question as a separate trial with flat structure
    api.recordPageData({
      question: q.id,
      skipped: response.isSkipped,
      response: normalizedResponse,
    })
  })

  api.goNextView()
}
</script>

<template>
  <ConstrainedTaskWindow
    variant="ghost"
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <div class="w-[80%] max-w-3xl mx-auto flex flex-col h-full py-8">
      <!-- Header with page indicator -->
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold">
          <i-material-symbols-verified-user-outline class="inline-block mr-2 text-3xl" /> Attention Check
        </h1>
        <Badge variant="secondary" class="text-base px-4 py-1">
          Question {{ api.stepIndex + 1 }} of {{ api.length }}
        </Badge>
      </div>

      <!-- General instructions - visible on every page -->
      <div class="mb-6 py-4 px-0 bg-muted/30 rounded-lg">
        <p class="text-base text-muted-foreground leading-relaxed">
          To verify whether you were attentive throughout the experiment, please answer the following questions as well as possible.
          It is okay if you do not know the answer to some of the questions. In this case, you can simply skip the question.
        </p>
      </div>

      <!-- Question content -->
      <div class="flex-1 text-left">
        <div class="space-y-6">
          <p class="text-lg font-medium">{{ currentQuestion.question }}</p>

          <div class="space-y-4">
            <!-- Skip toggle -->
            <div class="flex items-center space-x-2 mb-4">
              <Switch :id="'skip-' + currentQuestion.id" v-model="api.persist.attentionResponses[currentQuestion.id].isSkipped" />
              <Label :for="'skip-' + currentQuestion.id" class="cursor-pointer font-normal opacity-70">Skip this question</Label>
            </div>

            <!-- Question Input UI -->
            <div v-if="!api.persist.attentionResponses[currentQuestion.id].isSkipped" class="max-w-md space-y-2">
              <div v-if="currentQuestion.help && !currentQuestion.multiSelect" class="text-xs text-muted-foreground">
                {{ currentQuestion.help }}
              </div>

              <!-- Multi-select -->
              <div v-if="currentQuestion.answers && currentQuestion.multiSelect">
                <MultiSelect
                  :options="currentQuestion.answers"
                  v-model="api.persist.attentionResponses[currentQuestion.id].userInput"
                  variant="default"
                  :help="currentQuestion.help || 'Select all that apply'"
                  size="lg"
                />
              </div>

              <!-- Single select dropdown -->
              <Select v-else-if="currentQuestion.answers" v-model="api.persist.attentionResponses[currentQuestion.id].userInput">
                <SelectTrigger class="w-full bg-background dark:bg-background text-base">
                  <SelectValue placeholder="Select an option" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="answer in currentQuestion.answers" :key="answer" :value="answer">
                    {{ answer }}
                  </SelectItem>
                </SelectContent>
              </Select>

              <!-- Text Input -->
              <template v-else>
                <Input
                  :id="'input-' + currentQuestion.id"
                  v-model="api.persist.attentionResponses[currentQuestion.id].userInput"
                  type="text"
                  :placeholder="currentQuestion.placeholder || 'Enter your answer...'"
                  :aria-invalid="hasInvalidInput(currentQuestion)"
                />
                <p v-if="hasInvalidInput(currentQuestion)" class="text-destructive text-sm font-medium mt-1">
                  {{ currentQuestion.errorMessage || 'Please provide a valid answer.' }}
                </p>
              </template>
            </div>

            <div v-else class="text-sm text-muted-foreground italic flex items-center">
              <i-lucide-skip-forward class="mr-1" /> Question skipped.
            </div>
          </div>
        </div>
      </div>

      <!-- Footer navigation -->
      <div class="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
        <Button variant="outline" :disabled="api.stepIndex === 0" @click="api.goPrevStep()">
          <i-fa6-solid-arrow-left class="mr-2" />
          Previous
        </Button>

        <!-- Page dots indicator -->
        <div class="flex gap-2">
          <div
            v-for="i in api.length"
            :key="i"
            class="w-2.5 h-2.5 rounded-full transition-all"
            :class="i - 1 === api.stepIndex ? 'bg-primary w-8' : 'bg-gray-300'"
          ></div>
        </div>

        <Button v-if="!api.isLastStep()" variant="default" :disabled="!isCurrentValid" @click="api.goNextStep()">
          Next
          <i-fa6-solid-arrow-right class="ml-2" />
        </Button>
        <Button v-else variant="default" :disabled="!isAllValid" @click="finish">
          Finish
          <i-fa6-solid-arrow-right class="ml-2" />
        </Button>
      </div>
    </div>
  </ConstrainedTaskWindow>
</template>
