<script setup>
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { ConstrainedTaskWindow } from '@/uikit/layouts'
import trialsData from './trials.json'
import adviceTrialsData from './advice_trials.json'

const props = defineProps({
  trialType: { type: String, default: 'type1' },
})

const api = useViewAPI()

// ── Select data source and keys based on trial type ───────────────────────────
// Types 1 & 2 → trials.json (description-based)
// Types 3 & 4 → advice_trials.json (advice-based)
// Types 2 & 4 → free-text response instead of slider
const isAdviceSource = props.trialType === 'type3' || props.trialType === 'type4'
const isTextInput    = props.trialType === 'type2' || props.trialType === 'type4'
const sourceData     = isAdviceSource ? adviceTrialsData : trialsData

const persistKey  = props.trialType === 'type1' ? 'participantTrialIds'
                  : `participantTrialIds_${props.trialType}`
const attemptsKey = props.trialType === 'type1' ? 'attempts'
                  : `attempts_${props.trialType}`

// ── Per-participant trial sampling ────────────────────────────────────────────
// Types 1 & 2: Fixed 10 from Pool A + all 10 from B/C/D = 20 trials, shuffled
// Types 3 & 4: all 20 shown, shuffled
const FIXED_POOL_A_IDS = [1, 3, 7, 13, 15]  // 2×addition_first, 1×left_to_right, 1×right_to_left, 1×bracket_ignorer

if (!api.persist.isDefined(persistKey)) {
  if (isAdviceSource) {
    const combined = [...sourceData].sort(() => Math.random() - 0.5)
    api.persist[persistKey] = combined.map(t => t.id)
  } else {
    const poolA   = sourceData.filter(t => FIXED_POOL_A_IDS.includes(t.id))
    const poolBCD = sourceData.filter(t => t.pool !== 'A')
    const combined = [...poolA, ...poolBCD].sort(() => Math.random() - 0.5)
    api.persist[persistKey] = combined.map(t => t.id)
  }
}

const idToTrial = Object.fromEntries(sourceData.map(t => [t.id, t]))

// Filter out stale IDs that no longer exist in the trial bank (e.g. from a previous session)
let participantTrials = api.persist[persistKey].map(id => idToTrial[id]).filter(t => t !== undefined)

// If all persisted IDs were stale, reset and re-sample
if (participantTrials.length === 0) {
  if (isAdviceSource) {
    const combined = [...sourceData].sort(() => Math.random() - 0.5)
    api.persist[persistKey] = combined.map(t => t.id)
  } else {
    const poolA   = sourceData.filter(t => FIXED_POOL_A_IDS.includes(t.id))
    const poolBCD = sourceData.filter(t => t.pool !== 'A')
    const combined = [...poolA, ...poolBCD].sort(() => Math.random() - 0.5)
    api.persist[persistKey] = combined.map(t => t.id)
  }
  participantTrials = api.persist[persistKey].map(id => idToTrial[id])
}

const TRIAL_COUNT = participantTrials.length   // 20 for types 1/2, 20 for types 3/4

// ── Build step list ───────────────────────────────────────────────────────────
// Randomly assign which 10 of 20 trials show trace-first vs together
const splitFlags = [...Array(10).fill(false), ...Array(10).fill(true)].sort(() => Math.random() - 0.5)

const trials = api.steps.append(
  participantTrials.map((t, i) => ({
    id: `trial_${t.id}`,
    trialData: t,
    showTraceFirst: splitFlags[i],
    response: null,
    comment: null,
    correct: null,
    rt: null,
  }))
)
trials.append([{ id: 'summary' }])

// Persistent counters (initialise all four so they always exist)
if (!api.persist.isDefined('score'))              api.persist.score = 0
if (!api.persist.isDefined('attempts'))           api.persist.attempts = 0
if (!api.persist.isDefined('attempts_type2'))     api.persist.attempts_type2 = 0
if (!api.persist.isDefined('attempts_type3'))     api.persist.attempts_type3 = 0
if (!api.persist.isDefined('attempts_type4'))     api.persist.attempts_type4 = 0

if (!api.isTimerStarted()) api.startTimer()

// ── Autofill for testing ──────────────────────────────────────────────────────
function autofill() {
  while (api.stepIndex < api.nSteps) {
    const step = api.stepData
    if (step.id !== 'summary') {
      const t = step.trialData
      if (isTextInput) {
        step.response = 'autofill response'
        step.correct  = null
        step.rt       = api.faker.rnorm(4000, 800)
        api.persist[attemptsKey] += 1
      } else if (t.format === 'type1_yn') {
        const LIKERT_OPTIONS = ['Strongly Agree', 'Agree', 'Somewhat Agree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree']
        step.response = LIKERT_OPTIONS[Math.floor(Math.random() * LIKERT_OPTIONS.length)]
        step.correct  = null
        step.rt       = api.faker.rnorm(4000, 800)
        api.persist[attemptsKey] += 1
      } else if (t.format === 'advice_slider') {
        step.response = Math.round(Math.max(0, Math.min(10, api.faker.rnorm(5, 2))))
        step.correct  = null
        step.rt       = api.faker.rnorm(4000, 800)
        api.persist[attemptsKey] += 1
      } else {
        step.response = t.options[0].key
        step.correct  = t.options[0].key === t.correctKey ? 1 : 0
        step.rt       = api.faker.rnorm(4000, 800)
        api.persist.score += step.correct
        api.persist[attemptsKey] += 1
      }
    }
    api.recordStep()
    api.goNextStep()
  }
}
api.setAutofill(autofill)

// ── Per-trial reactive state ──────────────────────────────────────────────────
import { ref, computed, watch } from 'vue'

const LIKERT_OPTIONS = ['Strongly Agree', 'Agree', 'Somewhat Agree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree']

const selectedKey    = ref(null)
const submitted      = ref(false)
const likertValue    = ref(null)
const sliderValue    = ref(5)
const textResponse   = ref('')
const traceViewed    = ref(false)

watch(
  () => api.stepIndex,
  () => {
    selectedKey.value  = null
    submitted.value    = false
    likertValue.value  = null
    sliderValue.value  = 5
    textResponse.value = ''
    traceViewed.value  = false
    api.startTimer()
  }
)

const currentTrial    = computed(() => api.stepData?.trialData ?? null)
const isSummary       = computed(() => api.stepData?.id === 'summary')
const showTraceFirst  = computed(() => api.stepData?.showTraceFirst ?? false)
const inTracePhase    = computed(() => showTraceFirst.value && !traceViewed.value)
const isLikert        = computed(() => !isTextInput && currentTrial.value?.format === 'type1_yn')
const isAdviceSlider  = computed(() => !isTextInput && currentTrial.value?.format === 'advice_slider')
const canSubmit = computed(() => {
  if (isTextInput)        return textResponse.value.trim().length > 0
  if (isLikert.value)     return likertValue.value !== null
  if (isAdviceSlider.value) return true
  return !!selectedKey.value
})

const localQuestionNumber = computed(() => api.stepIndex + 1)

function submitAnswer() {
  if (submitted.value || !canSubmit.value) return
  submitted.value = true
  const rt = api.elapsedTime()
  if (isTextInput) {
    api.stepData.response = textResponse.value.trim()
    api.stepData.correct  = null
    api.stepData.rt       = rt
    api.persist[attemptsKey] += 1
  } else if (isLikert.value) {
    api.stepData.response     = likertValue.value
    api.stepData.comment      = textResponse.value.trim()
    api.stepData.correct      = null
    api.stepData.rt           = rt
    api.persist[attemptsKey] += 1
  } else if (isAdviceSlider.value) {
    api.stepData.response = sliderValue.value
    api.stepData.correct  = null
    api.stepData.rt       = rt
    api.persist[attemptsKey] += 1
  } else {
    api.stepData.response = selectedKey.value
    api.stepData.correct  = selectedKey.value === currentTrial.value.correctKey ? 1 : 0
    api.stepData.rt       = rt
    api.persist.score    += api.stepData.correct
    api.persist[attemptsKey] += 1
  }
  api.recordStep()
  api.goNextStep()
}

function nextTrial() { api.goNextStep() }
function finish()    { api.goNextView() }

const FORMAT_LABELS = {
  type1_yn:       'Identify the misconception',
  full_trace:     'Full trace of student work',
  blanked_wrong:  'Student work (some steps hidden)',
  advice_opinion: 'Would this help?',
  advice_slider:  'Rate the advice',
}

const SUMMARY_MESSAGES = {
  type1: (n) => `You rated ${n} descriptions.`,
  type2: (n) => `You described ${n} student responses.`,
  type3: (n) => `You rated ${n} pieces of advice.`,
  type4: (n) => `You gave advice for ${n} students.`,
}
</script>

<template>
  <ConstrainedTaskWindow
    variant="ghost"
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <!-- ── Summary screen ───────────────────────────────────────────────────── -->
    <div v-if="isSummary" class="flex flex-col items-center justify-center h-full gap-6 text-center px-8">
      <h2 class="text-2xl font-bold">All done!</h2>
      <p class="text-lg text-muted-foreground">
        {{ SUMMARY_MESSAGES[props.trialType]?.(api.persist[attemptsKey]) }}
      </p>
      <Button size="lg" @click="finish()">Continue</Button>
    </div>

    <!-- ── Trial screen ─────────────────────────────────────────────────────── -->
    <div v-else-if="currentTrial" class="flex flex-col gap-5 px-8 py-6 w-full max-w-2xl mx-auto h-full overflow-y-auto">

      <!-- Progress -->
      <div class="flex items-center justify-between text-sm text-muted-foreground">
        <span>Question {{ localQuestionNumber }} of {{ TRIAL_COUNT }}</span>
        <span class="capitalize text-xs bg-muted px-2 py-1 rounded">
          {{ FORMAT_LABELS[currentTrial.format] ?? currentTrial.format }}
        </span>
      </div>
      <div class="w-full bg-muted rounded-full h-1.5">
        <div
          class="bg-primary h-1.5 rounded-full transition-all"
          :style="{ width: ((localQuestionNumber - 1) / TRIAL_COUNT * 100) + '%' }"
        />
      </div>

      <!-- Expression (hidden on question screen for split trials) -->
      <div v-if="!showTraceFirst || inTracePhase">
        <p class="text-sm text-muted-foreground mb-1">
           {{ currentTrial.studentName }} is a third grade student. Here is the expression given to {{ currentTrial.studentName }}, in their math test.:
        </p>
        <p class="text-2xl font-mono font-semibold">{{ currentTrial.expression }}</p>
      </div>

      <!-- Final answer + trace (hidden on question screen for split trials) -->
      <div v-if="!showTraceFirst || inTracePhase">
        <p class="text-sm text-muted-foreground mb-2">
          Here is the final answer {{ currentTrial.studentName }} produced, along with their working:
        </p>
        <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7 whitespace-pre">
          <div v-for="(line, i) in currentTrial.traceLines" :key="i">
            <span
              v-if="line === '████████████████████'"
              class="inline-block bg-gray-800 text-gray-800 rounded select-none px-1"
              title="This step is hidden"
            >████████████████████</span>
            <span v-else-if="line === '↓'" class="text-muted-foreground">  =</span>
            <span v-else-if="line === '...'" class="text-muted-foreground">  ...</span>
            <span v-else>{{ line }}</span>
          </div>
        </div>
      </div>

      <!-- Description box (type1_yn — Type 1 only, hidden during trace phase) -->
      <div v-if="currentTrial.format === 'type1_yn' && !isTextInput && !inTracePhase"
           class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-900">
        <p class="italic">"{{ currentTrial.descriptionShown }}"</p>
      </div>

      <!-- Advice box (advice_slider — Type 3 only) -->
      <div v-if="(currentTrial.format === 'advice_opinion' || currentTrial.format === 'advice_slider') && !isTextInput"
           class="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 text-sm text-blue-900">
        <p class="font-medium mb-1">Advice given to {{ currentTrial.studentName }}:</p>
        <p class="italic">"{{ currentTrial.advice }}"</p>
      </div>

      <!-- Question + options (full_trace, blanked_wrong, advice_opinion only) -->
      <div v-if="currentTrial.format !== 'advice_slider' && currentTrial.format !== 'type1_yn'" class="flex flex-col gap-3 flex-1">
        <p class="text-sm font-medium">
          <template v-if="currentTrial.format === 'full_trace'">What rule did this student follow?</template>
          <template v-else-if="currentTrial.format === 'blanked_wrong'">What went wrong in the hidden step?</template>
          <template v-else-if="currentTrial.format === 'advice_opinion'">Will this advice help {{ currentTrial.studentName }} learn to solve this type of problem correctly?</template>
        </p>
        <div class="flex flex-col gap-3">
          <button
            v-for="opt in currentTrial.options"
            :key="opt.key"
            :disabled="submitted"
            @click="selectedKey = opt.key"
            class="text-left rounded-lg border px-4 py-3 text-sm transition-colors"
            :class="{
              'border-primary bg-primary/10 ring-1 ring-primary': selectedKey === opt.key && !submitted,
              'border-green-500 bg-green-100 ring-1 ring-green-500 text-green-900':
                submitted && currentTrial.correctKey && opt.key === currentTrial.correctKey,
              'border-red-400 bg-red-100 text-red-900':
                submitted && currentTrial.correctKey && selectedKey === opt.key && opt.key !== currentTrial.correctKey,
              'border-primary bg-primary/10 ring-1 ring-primary':
                submitted && !currentTrial.correctKey && opt.key === selectedKey,
              'border-muted-foreground/20 hover:border-primary/50 hover:bg-muted/50':
                !submitted && selectedKey !== opt.key,
              'opacity-40': submitted && currentTrial.correctKey && opt.key !== currentTrial.correctKey && selectedKey !== opt.key,
            }"
          >
            <span v-if="currentTrial.format === 'advice_opinion'" class="font-medium">{{ opt.label }}</span>
            <span v-else class="text-sm">{{ opt.description }}</span>
          </button>
        </div>
      </div>

      <!-- Free-text input (Types 2 and 4) -->
      <div v-if="isTextInput" class="flex flex-col gap-3 flex-1">
        <p class="text-sm font-medium">
          <template v-if="props.trialType === 'type2'">What do you think the student did here?</template>
          <template v-else>What advice would you give this student to make them do better?</template>
        </p>
        <textarea
          v-model="textResponse"
          :disabled="submitted"
          placeholder="Type your response here…"
          rows="4"
          class="w-full rounded-lg border border-input bg-background px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
        />
        <div v-if="submitted" class="text-sm text-muted-foreground">
          Response recorded.
        </div>
      </div>

      <!-- Likert radio buttons + comment (type1_yn — Type 1, hidden during trace phase) -->
      <div v-if="isLikert && !inTracePhase" class="flex flex-col gap-4 flex-1">
        <div class="flex flex-col gap-2">
          <p class="text-sm font-medium">Does this description capture the rule {{ currentTrial.studentName }} seems to be following?</p>
          <label
            v-for="option in LIKERT_OPTIONS"
            :key="option"
            class="flex items-center gap-3 rounded-lg border px-4 py-3 text-sm cursor-pointer transition-colors"
            :class="{
              'border-primary bg-primary/10': likertValue === option,
              'border-muted-foreground/20 hover:border-primary/50 hover:bg-muted/50': likertValue !== option,
              'opacity-60 pointer-events-none': submitted,
            }"
          >
            <input
              type="radio"
              :value="option"
              v-model="likertValue"
              :disabled="submitted"
              class="accent-primary"
            />
            {{ option }}
          </label>
        </div>
        <div class="flex flex-col gap-2">
          <p class="text-sm font-medium">
            What do you think {{ currentTrial.studentName }} did?
            <span class="text-muted-foreground font-normal">(optional)</span>
          </p>
          <textarea
            v-model="textResponse"
            :disabled="submitted"
            placeholder="Type your thoughts here…"
            rows="3"
            class="w-full rounded-lg border border-input bg-background px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
          />
        </div>
      </div>

      <!-- Slider (advice_slider — Type 3) -->
      <div v-if="isAdviceSlider" class="flex flex-col gap-4 flex-1">
        <p class="text-sm font-medium">How helpful do you think this advice will be for {{ currentTrial.studentName }}?</p>
        <div class="flex flex-col gap-2 px-1">
          <input
            type="range"
            min="0"
            max="10"
            step="1"
            v-model.number="sliderValue"
            :disabled="submitted"
            class="w-full h-2 cursor-pointer accent-primary disabled:opacity-60"
          />
          <div class="flex justify-between items-center text-xs">
            <span class="text-muted-foreground">0 — Not helpful at all</span>
            <span class="text-2xl font-bold text-foreground tabular-nums">{{ sliderValue }}</span>
            <span class="text-muted-foreground">10 — Extremely helpful</span>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pb-2">
        <Button v-if="inTracePhase" @click="traceViewed = true">
          Next
        </Button>
        <Button
          v-else
          :disabled="!canSubmit"
          @click="submitAnswer()"
        >
          Submit
        </Button>
      </div>
    </div>
  </ConstrainedTaskWindow>
</template>
