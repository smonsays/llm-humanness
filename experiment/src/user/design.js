/**
 * @file design.js
 * @description Configures the overall logic and timeline of the experiment.
 * The timeline defines the sequence of phases that the experiment goes through.
 * This file configures which phases occur in what order.
 *
 * Key documentation:
 * - Views: docs/coding/views.md
 * - Timeline: docs/coding/timeline.md
 * - Randomization: docs/coding/randomization.md
 *
 * @module design
 */

import { markRaw } from 'vue'
import { processQuery } from '@/core/utils/utils'

// 1. Import main built-in View components
import AdvertisementView from '@/user/components/AdvertisementView.vue'
import InformedConsentView from '@/builtins/informedConsent/InformedConsentView.vue'
import DemographicSurveyView from '@/user/components/DemographicSurveyView.vue'
import DeviceSurveyView from '@/builtins/deviceSurvey/DeviceSurveyView.vue'
import InstructionsView from '@/user/components/InstructionsView.vue'
import InstructionsQuizView from '@/builtins/instructionsQuiz/InstructionsQuiz.vue'
import AttentionCheckView from '@/user/components/AttentionCheckView.vue'
import DebriefView from '@/builtins/debrief/DebriefView.vue'
import TaskFeedbackSurveyView from '@/builtins/taskFeedbackSurvey/TaskFeedbackSurveyView.vue'
import ThanksView from '@/builtins/thanks/ThanksView.vue'
import WithdrawView from '@/builtins/withdraw/WithdrawView.vue'
import WindowSizerView from '@/builtins/windowSizer/WindowSizerView.vue'

// 2. Import user View components
import WorkingMemoryExpView from '@/user/components/working_memory_exp/WorkingMemoryExpView.vue'

// #3. Import smile API and timeline
import useAPI from '@/core/composables/useAPI'
const api = useAPI()

import Timeline from '@/core/timeline/Timeline'
const timeline = new Timeline(api)

// #4.  Set runtime configuration options
//      See http://smile.gureckislab.org/configuration.html#experiment-options-env
api.setRuntimeConfig('allowRepeats', false)

api.setRuntimeConfig('colorMode', 'light')
api.setRuntimeConfig('responsiveUI', true)

api.setRuntimeConfig('windowsizerRequest', { width: 800, height: 600 })
api.setRuntimeConfig('windowsizerAggressive', true)

api.setRuntimeConfig('anonymousMode', false)
api.setRuntimeConfig('labURL', 'https://lake-lab.github.io/')
api.setRuntimeConfig('brandLogoFn', 'universitylogo.png')

api.setRuntimeConfig('maxWrites', 1000)
api.setRuntimeConfig('minWriteInterval', 1000)
api.setRuntimeConfig('autoSave', true)

// Runtime config values for the consent form
api.setRuntimeConfig('estimated_time', '15 minutes')
api.setRuntimeConfig('payrate', '$4.00')

// set the informed consent text on the menu bar
import InformedConsentText from './components/InformedConsentText.vue'
api.setAppComponent('informed_consent_text', InformedConsentText)

// #5. Add between-subjects condition assignment
// This is where you can define conditions to which each participant should be assigned

// You can assign conditions by passing a javascript object to api.randomAssignCondition(),
// where the key is the condition name and the value is an array of possible condition values.
// Each unique condition manipulation should be assigned via a separate call to setConditions.

// EXAMPLE: set a between-subjects condition called taskOrder (AB or BA)
// api.randomAssignCondition({
//   taskOrder: ['AB', 'BA'],
// })

// #6. Define and add some routes to the timeline
// Each route should map to a View component.
// Each needs a name
// but for most experiments they go in sequence from the begining
// to the end of this list

// by default routes have meta.requiresConsent = true (unless you manually override it)
// by default routes have meta.requiresDone = false (unless you manually override it)

// IMPORTANT: A least one route needs to be called 'welcome_anonymous'
// to handle the landing case for someone not coming from a recruitment service

// First welcome screen for non-referral
timeline.pushSeqView({
  path: '/welcome',
  name: 'welcome_anonymous',
  component: AdvertisementView,
  meta: {
    prev: undefined,
    next: 'consent',
    allowAlways: true,
    requiresConsent: false,
  }, // override what is next
  beforeEnter: (to) => {
    api.getBrowserFingerprint()
  },
})

// welcome screen for referral from a service (e.g., prolific)
timeline.pushSeqView({
  path: '/welcome/:service',
  name: 'welcome_referred',
  component: AdvertisementView,
  meta: {
    prev: undefined,
    next: 'consent',
    allowAlways: true,
    requiresConsent: false,
  },
  beforeEnter: (to) => {
    // processes info to get the service-specific
    // participant info (e.g., Profilic ID)
    processQuery(to.query, to.params.service)
    api.getBrowserFingerprint()
  },
})

// consent
timeline.pushSeqView({
  name: 'consent',
  component: InformedConsentView,
  props: {
    informedConsentText: markRaw(InformedConsentText), // provide the informed consent text
  },
  meta: {
    requiresConsent: false,
    setConsented: true,
  },
})

// demographic survey
timeline.pushSeqView({
  name: 'demograph',
  component: DemographicSurveyView,
})

// windowsizer
timeline.pushSeqView({
  name: 'windowsizer',
  component: WindowSizerView,
})

// instructions
timeline.pushSeqView({
  name: 'instructions',
  component: InstructionsView,
})

// import the quiz questions
import { QUIZ_QUESTIONS } from './components/quizQuestions'
// instructions quiz
timeline.pushSeqView({
  name: 'quiz',
  component: InstructionsQuizView,
  props: {
    questions: QUIZ_QUESTIONS,
    returnTo: 'instructions',
    randomizeQandA: true,
  },
})

// main experiment

// working memory practice
timeline.pushSeqView({
  name: 'working_memory_practice',
  component: WorkingMemoryExpView,
  props: {
    nTrials: 4,
    minTrialLength: 3,
    maxTrialLength: 6,
    isPractice: true,
    instructionTitle: 'Practice: Working Memory Task',
    instructionSubtitle: 'This is a practice round to help you get used to the task.',
    buttonText: 'Start Practice',
  },
})

// working memory exp
timeline.pushSeqView({
  name: 'working_memory',
  component: WorkingMemoryExpView,
  props: {
    nTrials: 20,
    minTrialLength: 3,
    maxTrialLength: 12,
    instructionSubtitle: 'The real experiment starts, get ready!',
    isPractice: false,
  },
})

// attention check
timeline.registerView({
  name: 'attention_check_voro',
  component: AttentionCheckView,
  props: {
    questions: ['easy_modality', 'hard_voro', 'easy_input_method', 'easy_external_aid'],
  },
})

timeline.registerView({
  name: 'attention_check_maori',
  component: AttentionCheckView,
  props: {
    questions: ['easy_modality', 'hard_maori', 'easy_input_method', 'easy_external_aid'],
  },
})

timeline.registerView({
  name: 'attention_check_decimal',
  component: AttentionCheckView,
  props: {
    questions: ['easy_modality', 'hard_decimal', 'easy_input_method', 'easy_external_aid'],
  },
})

timeline.pushRandomizedNode({
  name: 'attention_check_random',
  options: [['attention_check_voro'], ['attention_check_maori'], ['attention_check_decimal']],
})

// debriefing form
// import DebriefText from '@/user/components/DebriefText.vue'
// timeline.pushSeqView({
//   name: 'debrief',
//   component: DebriefView,
//   props: {
//     debriefText: markRaw(DebriefText),
//   },
// })

// device survey
timeline.pushSeqView({
  name: 'device',
  component: DeviceSurveyView,
})

// feedback form
timeline.pushSeqView({
  name: 'feedback',
  component: TaskFeedbackSurveyView,
  meta: { setDone: true }, // this is the last form
})

// thanks/submit page
timeline.pushSeqView({
  name: 'thanks',
  component: ThanksView,
  meta: {
    requiresDone: true,
    resetApp: api.getConfig('allowRepeats'),
  },
})

// this is a special page that is for a withdraw
timeline.registerView({
  name: 'withdraw',
  meta: {
    requiresWithdraw: true,
    resetApp: api.getConfig('allowRepeats'),
  },
  component: WithdrawView,
})

timeline.build()

export default timeline
