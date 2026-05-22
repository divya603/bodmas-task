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

const examples = [
  {
    // Example 1: 1 misconception, correct description, trace shown → Strongly Agree / Agree
    expression: '3 + 4 × 5',
    traceLines: ['3 + 4 × 5', '↓', '7 × 5', '↓', '35'],
    studentName: 'Alex',
    belief: 'do addition before multiplication',
    traceHiddenInPhase2: false,
    correctAnswers: ['Strongly Agree', 'Agree'],
    correctFeedback: 'Correct! Alex added 3+4=7 before multiplying by 5, which shows they believe addition should come before multiplication. Strongly Agree or Agree are the best choices here.',
    incorrectFeedback: 'Not quite. Look at Alex\'s first step — they added 3+4=7 before multiplying, which is exactly what the statement describes. Strongly Agree or Agree would be the best choices here.',
  },
  {
    // Example 2: 2 misconceptions, description points to 1st error, trace shown → Somewhat Agree
    expression: '3 + 2² × (4 - 1)',
    traceLines: ['3 + 2² × (4-1)', '↓', '5² × (4-1)', '↓', '25 × (4-1)', '↓', '25 × 4 - 1', '↓', '100 - 1', '↓', '99'],
    studentName: 'Sam',
    belief: 'add before applying the exponent',
    traceHiddenInPhase2: false,
    correctAnswers: ['Somewhat Agree'],
    correctFeedback: 'Good thinking! The statement correctly captures one of Sam\'s errors — they did add 3+2=5 before squaring (step 2). However, Sam also dropped the brackets around (4-1) in step 4, which the statement doesn\'t mention. Since it only describes part of what happened, Somewhat Agree is the best choice.',
    incorrectFeedback: 'Take another look. The statement is partly right — Sam did add before the exponent (3+2=5²). But Sam also made a second error: dropping the brackets (4-1) in step 4. Because the statement only captures one of two errors, Somewhat Agree is the most accurate choice.',
  },
  {
    // Example 3: 1 misconception, foil (wrong) description, trace hidden → Disagree / Strongly Disagree
    expression: '5 - (2 - 7)',
    traceLines: ['5 - (2 - 7)', '↓', '5 - (-5)', '↓', '5 - 5', '↓', '0'],
    studentName: 'Jordan',
    belief: 'work right to left when two operations have the same priority',
    traceHiddenInPhase2: true,
    correctAnswers: ['Disagree', 'Strongly Disagree'],
    correctFeedback: 'Correct! Jordan\'s actual error was about negative signs — they treated 5−(−5) as 5−5 instead of 5+5. The statement describes a completely different mistake, so Disagree or Strongly Disagree are the right choices.',
    incorrectFeedback: 'Not quite. Jordan\'s error was about negative signs — they kept the minus when subtracting a negative number, turning 5−(−5) into 5−5. The statement describes something different entirely, so Disagree or Strongly Disagree would be the best choices.',
  },
]

// pages 1,2 → example 0; pages 3,4 → example 1; pages 5,6 → example 2
const exampleIndex  = computed(() => Math.floor((page.value - 1) / 2))
const isPhase1      = computed(() => page.value > 0 && (page.value - 1) % 2 === 0)
const currentExample = computed(() => examples[Math.max(0, exampleIndex.value)])

const isCorrect = computed(() => {
  const sel = demoSelections.value[exampleIndex.value]
  if (!sel) return null
  return currentExample.value.correctAnswers.includes(sel)
})

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
              class="flex flex-col items-center gap-2 flex-1 cursor-pointer"
            >
              <input type="radio" :value="option" v-model="demoSelections[exampleIndex]" class="accent-primary w-4 h-4" />
              <span class="text-xs text-center leading-tight text-muted-foreground">{{ option }}</span>
            </label>
          </div>
        </div>

        <!-- Feedback -->
        <div v-if="demoSelections[exampleIndex]"
             class="rounded-lg px-4 py-3 text-sm"
             :class="isCorrect
               ? 'bg-green-50 border border-green-200 text-green-900'
               : 'bg-red-50 border border-red-200 text-red-900'">
          <p class="font-semibold mb-1">{{ isCorrect ? '✓ Good answer!' : '✗ Not quite.' }}</p>
          <p>{{ isCorrect ? currentExample.correctFeedback : currentExample.incorrectFeedback }}</p>
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
