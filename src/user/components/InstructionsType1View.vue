<script setup>
import { ref, computed } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { ConstrainedTaskWindow } from '@/uikit/layouts'

const api = useViewAPI()

const LIKERT_OPTIONS = ['Strongly Agree', 'Agree', 'Somewhat Agree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree']

const page = ref(0)
const TOTAL_PAGES = 7  // 0 = intro, then 2 pages per example × 3 examples

const demoTextResponses = ref(['', '', ''])
const demoSelections    = ref([null, null, null])

const LIKERT_MEANING = {
  'Strongly Agree':    "you fully agree and think this statement perfectly describes what the student believes",
  'Agree':             "you mostly agree and think this statement largely matches the student's thinking",
  'Somewhat Agree':    "you partially agree and think this statement captures something but not the full picture",
  'Somewhat Disagree': "you partially disagree and think this statement is somewhat off from what the student did",
  'Disagree':          "you mostly disagree and think this statement doesn't really match the student's thinking",
  'Strongly Disagree': "you fully disagree and think this statement doesn't describe the student at all",
}

const examples = [
  {
    // Example 1: 1 misconception, correct belief statement, trace shown
    expression: '3 + 4 × 5',
    traceLines: ['3 + 4 × 5', '↓', '7 × 5', '↓', '35'],
    studentName: 'Alex',
    belief: 'do addition before multiplication',
    traceHiddenInPhase2: false,
    explanation: {
      errorDesc: "In the first step, Alex computed 3+4=7 before multiplying. They added first instead of multiplying first.",
      beliefDesc: "The belief statement describes this error exactly.",
      numMisconceptions: 1,
    },
  },
  {
    // Example 2: 2 misconceptions, belief points to 1st error, trace shown
    expression: '3 + 2² × (4 - 1)',
    traceLines: ['3 + 2² × (4-1)', '↓', '5² × (4-1)', '↓', '25 × (4-1)', '↓', '25 × 4 - 1', '↓', '100 - 1', '↓', '99'],
    studentName: 'Sam',
    belief: 'add before applying the exponent',
    traceHiddenInPhase2: false,
    explanation: {
      errorDesc: "Sam made two errors. In step 2, Sam added 3+2=5 before squaring. In step 4, Sam dropped the brackets around (4−1) and treated it as 25×4−1 instead of 25×3.",
      beliefDesc: "The belief statement correctly identifies Sam's first error but does not mention the second one. It captures one of the two misconceptions Sam has.",
      numMisconceptions: 2,
    },
  },
  {
    // Example 3: 1 misconception, foil belief statement, trace hidden
    expression: '5 - (2 - 7)',
    traceLines: ['5 - (2 - 7)', '↓', '5 - (-5)', '↓', '5 - 5', '↓', '0'],
    studentName: 'Jordan',
    belief: 'work right to left when two operations have the same priority',
    traceHiddenInPhase2: true,
    explanation: {
      errorDesc: "Jordan's error was about negative signs. In step 3, Jordan treated 5−(−5) as 5−5=0 instead of 5+5=10, not keeping the sign change when subtracting a negative.",
      beliefDesc: "The belief statement describes a completely different kind of error that Jordan did not make. It does not match what Jordan actually did.",
      numMisconceptions: 1,
    },
  },
]

// pages 1,2 → example 0; pages 3,4 → example 1; pages 5,6 → example 2
const exampleIndex   = computed(() => Math.floor((page.value - 1) / 2))
const isPhase1       = computed(() => page.value > 0 && (page.value - 1) % 2 === 0)
const currentExample = computed(() => examples[Math.max(0, exampleIndex.value)])

function next() {
  if (page.value < TOTAL_PAGES - 1) {
    page.value++
  } else {
    api.goFirstStep()
    api.goNextView()
  }
}
</script>

<template>
  <ConstrainedTaskWindow
    variant="ghost"
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <div class="flex flex-col gap-5 px-8 py-6 w-full max-w-2xl mx-auto h-full overflow-y-auto">

      <!-- ── Page 0: Introduction ──────────────────────────────────────────── -->
      <template v-if="page === 0">
        <h1 class="text-2xl font-bold">📋 Instructions</h1>

        <p class="text-base leading-relaxed">
          You'll see step-by-step solutions from a series of different students 🧑‍🎓 and try to figure out what each one thinks about how math works. Each trial has two steps.
        </p>

        <div class="bg-muted rounded-lg px-5 py-4 text-sm space-y-4">
          <div>
            <p class="font-semibold mb-1">👀 Step 1</p>
            <p>You'll see a math expression and one student's step-by-step solution. Write your initial thoughts about what they did. ✏️ Note: each student's individual arithmetic is correct — there are no calculation mistakes. Any errors are in the order they choose to apply operations.</p>
          </div>
          <div>
            <p class="font-semibold mb-1">💭 Step 2</p>
            <p>You'll see a statement about what this student might believe. Rate it on this scale. Keep in mind: a student may have made more than one type of error, and the statement might only describe one of them — use your best judgment about how well it fits overall.</p>
            <div class="mt-2 space-y-1 pl-2">
              <p><span class="font-semibold">Strongly Agree</span> — perfectly describes their belief</p>
              <p><span class="font-semibold">Agree</span> — mostly matches</p>
              <p><span class="font-semibold">Somewhat Agree</span> — partly matches</p>
              <p><span class="font-semibold">Somewhat Disagree</span> — somewhat off</p>
              <p><span class="font-semibold">Disagree</span> — mostly off</p>
              <p><span class="font-semibold">Strongly Disagree</span> — doesn't describe them at all</p>
            </div>
          </div>
        </div>

        <p class="text-base leading-relaxed">
          ⚠️ In Step 2, the student's work may or may not still be visible. You won't know in advance, so pay close attention in Step 1!
        </p>

        <div class="bg-amber-50 border border-amber-200 rounded-lg px-5 py-4 text-sm text-amber-900">
          <p class="font-semibold mb-1">Performance bonus</p>
          <p>Each statement has a correct answer — some descriptions accurately capture what the student misunderstands, others don't. You'll earn a bonus based on how accurately you rate each one.</p>
        </div>

        <div class="flex justify-end pt-2">
          <Button @click="next()">Continue <i-fa6-solid-arrow-right class="ml-1" /></Button>
        </div>
      </template>

      <!-- ── Phase 1 (pages 1, 3, 5): expression + trace + text box ─────────── -->
      <template v-else-if="isPhase1">
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          Example {{ exampleIndex + 1 }} of 3 — Step 1
        </div>

        <div>
          <p class="text-sm text-muted-foreground mb-1">Expression given to {{ currentExample.studentName }}:</p>
          <p class="text-2xl font-mono font-semibold">{{ currentExample.expression }}</p>
        </div>

        <div>
          <p class="text-sm text-muted-foreground mb-2">{{ currentExample.studentName }}'s work:</p>
          <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7">
            <div v-for="(line, i) in currentExample.traceLines.filter(l => l !== '↓').slice(1)" :key="i">
              <span class="text-muted-foreground">= </span>{{ line }}
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <p class="text-sm font-medium">Does it seem like {{ currentExample.studentName }} misunderstands something, and if so, what?</p>
          <textarea
            v-model="demoTextResponses[exampleIndex]"
            placeholder="Type your thoughts here…"
            rows="3"
            class="w-full rounded-lg border border-input bg-background px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--"><i-fa6-solid-arrow-left class="mr-1" /> Back</Button>
          <Button :disabled="!demoTextResponses[exampleIndex].trim()" @click="next()">
            Continue <i-fa6-solid-arrow-right class="ml-1" />
          </Button>
        </div>
      </template>

      <!-- ── Phase 2 (pages 2, 4, 6): belief statement + Likert + feedback ──── -->
      <template v-else>
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          Example {{ exampleIndex + 1 }} of 3 — Step 2
          <span v-if="currentExample.traceHiddenInPhase2" class="ml-2 normal-case text-amber-700">In this example, the student's step-by-step work is hidden</span>
        </div>

        <!-- Expression always shown -->
        <div>
          <p class="text-sm text-muted-foreground mb-1">Expression given to {{ currentExample.studentName }}:</p>
          <p class="text-2xl font-mono font-semibold">{{ currentExample.expression }}</p>
        </div>

        <!-- Trace only if not hidden -->
        <div v-if="!currentExample.traceHiddenInPhase2">
          <p class="text-sm text-muted-foreground mb-2">{{ currentExample.studentName }}'s work:</p>
          <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7">
            <div v-for="(line, i) in currentExample.traceLines.filter(l => l !== '↓').slice(1)" :key="i">
              <span class="text-muted-foreground">= </span>{{ line }}
            </div>
          </div>
        </div>

        <!-- Belief statement -->
        <div class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-900">
          <p class="italic">{{ currentExample.studentName }} believes they should {{ currentExample.belief }}.</p>
        </div>

        <!-- Likert -->
        <div class="flex flex-col gap-3">
          <p class="text-sm font-medium">How much do you agree that this is what the student believes?</p>
          <div class="flex justify-between gap-2">
            <label
              v-for="option in [...LIKERT_OPTIONS].reverse()"
              :key="option"
              class="flex flex-col items-center gap-2 flex-1"
              :class="demoSelections[exampleIndex] ? 'cursor-default' : 'cursor-pointer'"
            >
              <input
                type="radio"
                :value="option"
                v-model="demoSelections[exampleIndex]"
                :disabled="demoSelections[exampleIndex] !== null"
                class="accent-primary w-4 h-4"
              />
              <span class="text-xs text-center leading-tight text-muted-foreground">{{ option }}</span>
            </label>
          </div>
        </div>

        <!-- Feedback -->
        <div v-if="demoSelections[exampleIndex]"
             class="rounded-lg px-4 py-3 text-sm bg-blue-50 border border-blue-200 text-blue-900 space-y-2">
          <p>{{ currentExample.explanation.errorDesc }}</p>
          <p>{{ currentExample.explanation.beliefDesc }}</p>
          <p v-if="currentExample.explanation.numMisconceptions === 2" class="text-blue-700 italic">
            Note: when a student has more than one error, the belief statement will point to one of them — rate how well it describes that specific aspect of their thinking.
          </p>
          <p class="border-t border-blue-200 pt-2">
            By selecting <span class="font-semibold">{{ demoSelections[exampleIndex] }}</span>,
            {{ LIKERT_MEANING[demoSelections[exampleIndex]] }}.
          </p>
        </div>

        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--"><i-fa6-solid-arrow-left class="mr-1" /> Back</Button>
          <Button :disabled="!demoSelections[exampleIndex]" @click="next()">
            {{ page === TOTAL_PAGES - 1 ? 'Start the task' : 'Continue' }} <i-fa6-solid-arrow-right class="ml-1" />
          </Button>
        </div>
      </template>

    </div>
  </ConstrainedTaskWindow>
</template>
