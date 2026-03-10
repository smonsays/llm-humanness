<script setup>
import { ref, onMounted } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { ConstrainedTaskWindow } from '@/uikit/layouts'

const props = defineProps({
  nTrials: {
    type: Number,
    default: 20,
  },
  isPractice: {
    type: Boolean,
    default: false,
  },
  instructionTitle: {
    type: String,
    default: 'Working Memory Task',
  },
  instructionSubtitle: {
    type: String,
    default: '',
  },
  instructionText: {
    type: String,
    default:
      'You will see lists of letters appearing one by one. After each list, you will be asked to recall one specific letter in the list.',
  },
  buttonText: {
    type: String,
    default: 'Start Experiment',
  },
  stimMs: {
    type: Number,
    default: 800,
  },
  isiMs: {
    type: Number,
    default: 300,
  },
  minTrialLength: {
    type: Number,
    default: 3,
  },
  maxTrialLength: {
    type: Number,
    default: 12,
  },
})

const api = useViewAPI()

// --- Validation ---
if (props.maxTrialLength - props.minTrialLength + 1 <= 0) {
  console.error(
    `WorkingMemoryExpView: maxTrialLength (${props.maxTrialLength}) must be greater than or equal to minTrialLength (${props.minTrialLength})`
  )
} else if (props.nTrials % (props.maxTrialLength - props.minTrialLength + 1) !== 0) {
  console.warn(
    `WorkingMemoryExpView: nTrials (${props.nTrials}) is not evenly divisible by the number of trial length levels (${props.maxTrialLength - props.minTrialLength + 1}). ` +
      `Trial lengths will not be perfectly balanced.`
  )
}

// --- State & Constants ---
const phase = ref('instructions') // instructions, fixation, list, recall, summary
const currentItem = ref('')
const userResponse = ref('') // The item currently selected by the participant

const itemPools = {
  letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
  // digits: '0123456789'.split(''),
}

function getOrdinal(n) {
  const s = ['th', 'st', 'nd', 'rd']
  const v = n % 100
  return n + (s[(v - 20) % 10] || s[v] || s[0])
}

// --- Trial Configuration ---
const trials = api.steps.append([
  {
    id: props.isPractice ? 'wm_practice' : 'wm_task',
    rt: () => api.faker.rnorm(1200, 400),
    hit: () => api.faker.rbinom(1, 0.8),
    response: () => api.faker.rchoice(itemPools[api.stepData.poolType]),
  },
])

const poolKeys = Object.keys(itemPools)
const probeTypes = ['association', 'position']

// The following attempts to balance the trial lengths which all fall into [minTrialLength, maxTrialLength]
// For this to be perfectly balanced, it needs to hold that nTrials % (maxTrialLength - minTrialLength + 1) == 0
const trialLengthList = api.shuffle(
  Array.from(
    { length: props.nTrials },
    (_, i) => (i % (props.maxTrialLength - props.minTrialLength + 1)) + props.minTrialLength
  )
)
const trialPoolList = api.shuffle(Array.from({ length: props.nTrials }, (_, i) => i % poolKeys.length))
const trialProbeList = api.shuffle(Array.from({ length: props.nTrials }, (_, i) => i % probeTypes.length))

const trialList = Array.from({ length: props.nTrials }, (_, i) => {
  const len = trialLengthList[i]
  const poolType = poolKeys[trialPoolList[i]]
  const probeType = probeTypes[trialProbeList[i]]
  const pool = itemPools[poolType]
  const itemList = api.sampleWithoutReplacement(pool, len)
  const targetIdx = api.randomInt(0, len - 1)
  return {
    id: `trial_${i}`,
    poolType,
    probeType,
    itemList,
    targetItem: itemList[targetIdx],
    targetIdx: targetIdx,
    promptPos: targetIdx + 1,
    precedingItem: targetIdx > 0 ? itemList[targetIdx - 1] : null,
  }
})
trials[0].append(trialList)
trials.append([{ id: 'summary' }])

// --- Persistent Data ---
// Use separate persistence keys for practice and real trials to avoid mixing scores
const scoreKey = props.isPractice ? 'wm_practice_score' : 'wm_score'
const totalKey = props.isPractice ? 'wm_practice_total' : 'wm_total'

if (!api.persist.isDefined(scoreKey)) {
  api.persist[scoreKey] = 0
  api.persist[totalKey] = 0
}

async function startTrial() {
  if (api.path[0] === 'summary') {
    phase.value = 'summary'
    return
  }

  userResponse.value = ''
  phase.value = 'fixation'
  await new Promise((r) => setTimeout(r, 800))

  phase.value = 'list'
  for (const item of api.stepData.itemList) {
    currentItem.value = item
    await new Promise((r) => setTimeout(r, props.stimMs))
    currentItem.value = ''
    await new Promise((r) => setTimeout(r, props.isiMs))
  }

  phase.value = 'recall'
  api.startTimer()
}

function submitResponse() {
  if (!userResponse.value) return

  const response = userResponse.value.toUpperCase()
  const hit = response === api.stepData.targetItem ? 1 : 0

  api.stepData.rt = api.elapsedTime()
  api.stepData.response = response
  api.stepData.hit = hit

  api.persist[scoreKey] += hit
  api.persist[totalKey] += 1

  api.recordStep()
  api.goNextStep()

  if (api.path[0] === 'summary') {
    phase.value = 'summary'
  } else {
    startTrial()
  }
}

// Global key listener
const allPossibleItems = Object.values(itemPools).flat()
const stopKeys = api.onKeyDown(
  [...allPossibleItems, ...allPossibleItems.map((l) => l.toLowerCase()), 'Enter'],
  (e) => {
    if (phase.value !== 'recall') return

    if (e.key === 'Enter') {
      submitResponse()
      return
    }

    // Otherwise, update the displayed response
    userResponse.value = e.key.toUpperCase()
  },
  { dedupe: true }
)

function finish() {
  stopKeys()
  api.goNextView()
}

// --- Autofill for Testing ---
api.setAutofill(() => {
  while (api.stepIndex < api.nSteps) {
    api.faker.render(api.stepData)
    if (api.stepData.hit) {
      api.persist[scoreKey] += api.stepData.hit.val
      api.persist[totalKey] += 1
    }
    api.recordStep()
    if (api.goNextStep() === null) break
  }
})

onMounted(() => {
  if (api.stepIndex > 0 || api.path[0] === 'summary') {
    startTrial()
  }
})
</script>

<template>
  <ConstrainedTaskWindow
    variant="ghost"
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <!-- Experimental Task Content -->
    <div class="text-center" v-if="api.path[0] === 'wm_task' || api.path[0] === 'wm_practice'">
      <!-- 0. Instructions -->
      <div v-if="phase === 'instructions'">
        <h1 class="text-3xl font-bold mb-4">{{ props.instructionTitle }}</h1>
        <p
          v-if="props.instructionSubtitle"
          class="text-xl mb-4 font-semibold text-muted-foreground"
          v-html="props.instructionSubtitle"
        ></p>
        <p class="text-lg mb-8 text-muted-foreground" v-html="props.instructionText"></p>
        <Button size="lg" @click="startTrial()">{{ props.buttonText }}</Button>
      </div>

      <!-- 1. Fixation -->
      <div v-else-if="phase === 'fixation'">
        <h1 class="text-6xl font-bold text-muted-foreground">+</h1>
      </div>

      <!-- 2. List Phase -->
      <div v-else-if="phase === 'list'">
        <h1 class="text-8xl font-mono font-bold">{{ currentItem }}</h1>
      </div>

      <!-- 3. Recall Phase -->
      <div v-else-if="phase === 'recall'">
        <template v-if="api.stepData.probeType === 'position'">
          <h2 class="text-3xl mb-8">
            What was the
            <span class="text-primary font-bold">{{ getOrdinal(api.stepData.promptPos) }}</span> letter?
          </h2>
        </template>
        <template v-else>
          <h2 class="text-3xl mb-8" v-if="api.stepData.targetIdx === 0">
            What was the <span class="text-primary font-bold">first</span> letter?
          </h2>
          <h2 class="text-3xl mb-8" v-else>
            What letter came after
            <span class="text-primary font-bold">{{ api.stepData.precedingItem }}</span
            >?
          </h2>
        </template>

        <div class="flex flex-col items-center justify-center gap-6">
          <div
            class="w-24 h-24 border-2 border-dashed border-muted-foreground rounded-lg flex items-center justify-center"
          >
            <span class="text-6xl font-mono font-bold text-primary">{{ userResponse }}</span>
          </div>

          <div class="space-y-2">
            <p v-if="!userResponse" class="text-xl text-muted-foreground italic">Press a key to select</p>
            <div v-else class="flex flex-col items-center gap-4">
              <p class="text-xl text-muted-foreground italic">Press Enter to confirm or another key to change</p>
              <Button size="lg" @click="submitResponse">Confirm Response</Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary / Completion Screen -->
    <div class="text-center" v-else>
      <h1 class="text-3xl font-bold mb-4">{{ props.isPractice ? 'Practice Completed' : 'Task Completed' }}</h1>
      <p class="text-xl text-muted-foreground mb-8">
        Your {{ props.isPractice ? 'practice' : 'final' }} score:
        {{ api.persist[totalKey] > 0 ? ((api.persist[scoreKey] / api.persist[totalKey]) * 100).toFixed(1) : 0 }}%
      </p>
      <Button variant="default" size="lg" @click="finish()">
        {{ props.isPractice ? 'Continue to Experiment' : 'Finish' }}
        <svg class="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </Button>
    </div>
  </ConstrainedTaskWindow>
</template>
