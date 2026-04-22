<script setup>
import { ref, computed } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { ConstrainedTaskWindow } from '@/uikit/layouts'

const api = useViewAPI()

const LIKERT_OPTIONS = ['Strongly Agree', 'Agree', 'Somewhat Agree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree']

const page = ref(0)
const TOTAL_PAGES = 5

// Per-example selected radio value (just for demo, not recorded)
const demoSelections = ref([null, null, null])

const examples = [
  {
    // Together condition, correct description
    expression: '3 + 4 × 5',
    traceLines: ['3 + 4 × 5', '↓', '7 × 5', '↓', '35'],
    studentName: 'Alex',
    description: 'Did addition/subtraction before multiplication/division.',
    hint: 'Alex got 35 instead of the correct answer (23). The description accurately captures what Alex did — so Agree or Strongly Agree would be appropriate here.',
  },
  {
    // Together condition, wrong description
    expression: '2 + 3 × 4',
    traceLines: ['2 + 3 × 4', '↓', '5 × 4', '↓', '20'],
    studentName: 'Sam',
    description: 'Evaluated right to left.',
    hint: 'Sam added first and got 20 (correct answer is 14). But the description says "right to left" — that doesn\'t match what Sam did. Disagree or Strongly Disagree would be appropriate here.',
  },
  {
    // Split condition — trace phase
    expression: '(3 + 4) × 5',
    traceLines: ['(3 + 4) × 5', '↓', '7 × 5', '↓', '35'],
    studentName: 'Jordan',
    description: 'Dropped the brackets.',
    hint: 'Jordan got 35, which is actually the correct answer here. The description says "dropped the brackets" — but Jordan evaluated the brackets correctly. Disagree or Strongly Disagree would be appropriate.',
  },
]

const currentExample  = computed(() => examples[Math.min(page.value - 1, examples.length - 1)])
const splitTracePhase = computed(() => page.value === 4) // page 4 = trace-only for example 3
const splitQuestionPhase = computed(() => page.value === 5) // unused — handled by TOTAL_PAGES

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
        <h1 class="text-2xl font-bold">Instructions</h1>

        <p class="text-base leading-relaxed">
          This study looks at whether people can examine a student's step-by-step working
          through a math equation and identify what rules or ideas the student may have
          misconceptions about.
        </p>

        <p class="text-base leading-relaxed">In each trial, you will see:</p>
        <ul class="list-disc pl-6 text-base leading-relaxed space-y-1">
          <li>A math expression given to a third-grade student</li>
          <li>The student's step-by-step working and final answer</li>
          <li>A proposed description of the rule the student seems to be following</li>
        </ul>

        <p class="text-base leading-relaxed">
          Your job is to rate <strong>how well the description captures the rule the student seems to be following</strong>,
          using a 6-point scale:
        </p>
        <div class="bg-muted rounded-lg px-5 py-4 text-sm space-y-1">
          <p><span class="font-semibold">Strongly Agree</span> — The description perfectly captures the rule the student is following.</p>
          <p><span class="font-semibold">Agree / Somewhat Agree</span> — The description mostly matches.</p>
          <p><span class="font-semibold">Somewhat Disagree / Disagree</span> — The description is off.</p>
          <p><span class="font-semibold">Strongly Disagree</span> — The description does not match at all.</p>
        </div>

        <p class="text-base leading-relaxed">
          You can also type any additional thoughts in a comment box below the rating.
        </p>

        <p class="text-base leading-relaxed">
          <strong>Note:</strong> Sometimes you will see the student's working and the question on the same screen.
          Other times you will see the working first, and the question will appear on a separate screen.
        </p>

        <div class="flex justify-end pt-2">
          <Button @click="next()">See examples <i-fa6-solid-arrow-right class="ml-1" /></Button>
        </div>
      </template>

      <!-- ── Pages 1–2: Together examples ─────────────────────────────────── -->
      <template v-else-if="page === 1 || page === 2">
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          Example {{ page }} of 3 — working and question shown together
        </div>

        <!-- Expression -->
        <div>
          <p class="text-sm text-muted-foreground mb-1">Expression given to {{ currentExample.studentName }}:</p>
          <p class="text-2xl font-mono font-semibold">{{ currentExample.expression }}</p>
        </div>

        <!-- Trace -->
        <div>
          <p class="text-sm text-muted-foreground mb-2">{{ currentExample.studentName }}'s working:</p>
          <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7 whitespace-pre">
            <div v-for="(line, i) in currentExample.traceLines" :key="i">
              <span v-if="line === '↓'" class="text-muted-foreground">  =</span>
              <span v-else>{{ line }}</span>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-900">
          <p class="italic">"{{ currentExample.description }}"</p>
        </div>

        <!-- Radio buttons -->
        <div class="flex flex-col gap-2">
          <p class="text-sm font-medium">Does this description capture the rule {{ currentExample.studentName }} seems to be following?</p>
          <label
            v-for="option in LIKERT_OPTIONS"
            :key="option"
            class="flex items-center gap-3 rounded-lg border px-4 py-3 text-sm cursor-pointer transition-colors"
            :class="{
              'border-primary bg-primary/10': demoSelections[page - 1] === option,
              'border-muted-foreground/20 hover:border-primary/50 hover:bg-muted/50': demoSelections[page - 1] !== option,
            }"
          >
            <input type="radio" :value="option" v-model="demoSelections[page - 1]" class="accent-primary" />
            {{ option }}
          </label>
        </div>

        <!-- Hint after selection -->
        <div v-if="demoSelections[page - 1]" class="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          {{ currentExample.hint }}
        </div>

        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--"><i-fa6-solid-arrow-left class="mr-1" /> Back</Button>
          <Button :disabled="!demoSelections[page - 1]" @click="next()">{{ page === 2 ? 'See split example' : 'Next example' }} <i-fa6-solid-arrow-right class="ml-1" /></Button>
        </div>
      </template>

      <!-- ── Page 3: Split example — trace screen ──────────────────────────── -->
      <template v-else-if="page === 3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          Example 3 of 3 — working shown first
        </div>

        <p class="text-sm text-muted-foreground">
          Sometimes you will only see the student's working on this screen.
          The question will appear on the next screen.
        </p>

        <!-- Expression -->
        <div>
          <p class="text-sm text-muted-foreground mb-1">Expression given to {{ examples[2].studentName }}:</p>
          <p class="text-2xl font-mono font-semibold">{{ examples[2].expression }}</p>
        </div>

        <!-- Trace -->
        <div>
          <p class="text-sm text-muted-foreground mb-2">{{ examples[2].studentName }}'s working:</p>
          <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7 whitespace-pre">
            <div v-for="(line, i) in examples[2].traceLines" :key="i">
              <span v-if="line === '↓'" class="text-muted-foreground">  =</span>
              <span v-else>{{ line }}</span>
            </div>
          </div>
        </div>

        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--"><i-fa6-solid-arrow-left class="mr-1" /> Back</Button>
          <Button @click="next()">Next <i-fa6-solid-arrow-right class="ml-1" /></Button>
        </div>
      </template>

      <!-- ── Page 4: Split example — question screen ───────────────────────── -->
      <template v-else-if="page === 4">
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          Example 3 of 3 — question screen (working is no longer shown)
        </div>

        <!-- Description -->
        <div class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-900">
          <p class="italic">"{{ examples[2].description }}"</p>
        </div>

        <!-- Radio buttons -->
        <div class="flex flex-col gap-2">
          <p class="text-sm font-medium">Does this description capture the rule {{ examples[2].studentName }} seems to be following?</p>
          <label
            v-for="option in LIKERT_OPTIONS"
            :key="option"
            class="flex items-center gap-3 rounded-lg border px-4 py-3 text-sm cursor-pointer transition-colors"
            :class="{
              'border-primary bg-primary/10': demoSelections[2] === option,
              'border-muted-foreground/20 hover:border-primary/50 hover:bg-muted/50': demoSelections[2] !== option,
            }"
          >
            <input type="radio" :value="option" v-model="demoSelections[2]" class="accent-primary" />
            {{ option }}
          </label>
        </div>

        <!-- Hint after selection -->
        <div v-if="demoSelections[2]" class="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          {{ examples[2].hint }}
        </div>

        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--"><i-fa6-solid-arrow-left class="mr-1" /> Back</Button>
          <Button :disabled="!demoSelections[2]" @click="next()">Start the task <i-fa6-solid-arrow-right class="ml-1" /></Button>
        </div>
      </template>

    </div>
  </ConstrainedTaskWindow>
</template>
